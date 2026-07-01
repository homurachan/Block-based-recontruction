import argparse
import shlex
from collections import OrderedDict

import mrcfile
import numpy as np


# changelog v4
# Add normalization
# changelog v5
# Add highpass filter
# changelog v5_no_starfile
# Remove the starfile/pandas dependency and use a lightweight text STAR parser.


def _split_star_line(line):
    """Split one ordinary STAR line while respecting single/double quotes."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return []
    if stripped.startswith(";"):
        raise ValueError(
            "Semicolon-delimited multiline STAR values are not supported by this "
            "lightweight parser. RELION optics/particles tables normally do not use them."
        )
    lexer = shlex.shlex(stripped, posix=True)
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _normalise_block_name(name):
    name = name.strip()
    if name.lower().startswith("data_"):
        name = name[5:]
    return name.lower()


def _normalise_label(label):
    return label.strip().lstrip("_").lower()


def read_star_text(filename):
    """
    Read a RELION-style STAR file without starfile/pandas.

    The returned object preserves block order and supports scalar items plus one or
    more loop_ tables per block. Ordinary quoted values are supported. The RELION
    data_optics/data_particles layout is fully supported.
    """
    with open(filename, "r", encoding="utf-8") as handle:
        lines = handle.readlines()

    star = {
        "preamble": [],
        "blocks": OrderedDict(),
    }
    current_block = None
    i = 0

    def ensure_block(block_name):
        if block_name not in star["blocks"]:
            star["blocks"][block_name] = {
                "items": [],
                "loops": [],
            }

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        lower = stripped.lower()

        if lower.startswith("data_"):
            current_block = stripped[5:].strip()
            ensure_block(current_block)
            i += 1
            continue

        if current_block is None:
            star["preamble"].append(raw.rstrip("\n"))
            i += 1
            continue

        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        if lower == "loop_":
            i += 1
            columns = []

            # Read loop column labels.
            while i < len(lines):
                header_line = lines[i].strip()
                if not header_line or header_line.startswith("#"):
                    i += 1
                    continue
                if not header_line.startswith("_"):
                    break
                tokens = _split_star_line(lines[i])
                if not tokens:
                    i += 1
                    continue
                columns.append(tokens[0])
                i += 1

            if not columns:
                raise ValueError(
                    f"Found loop_ without column labels in {filename} near line {i + 1}."
                )

            rows = []
            pending = []
            ncols = len(columns)

            # Read values. RELION normally stores one complete row per line, but
            # accumulating tokens also permits rows wrapped across ordinary lines.
            while i < len(lines):
                value_line = lines[i].strip()
                value_lower = value_line.lower()

                if value_lower.startswith("data_") or value_lower == "loop_" or value_lower.startswith("save_"):
                    break

                # A scalar tag marks the end of this loop.
                if value_line.startswith("_") and not pending:
                    break

                if not value_line or value_line.startswith("#"):
                    i += 1
                    continue

                tokens = _split_star_line(lines[i])
                pending.extend(tokens)

                while len(pending) >= ncols:
                    rows.append(pending[:ncols])
                    pending = pending[ncols:]

                i += 1

            if pending:
                raise ValueError(
                    f"Incomplete STAR loop row in {filename} near line {i + 1}: "
                    f"expected {ncols} values, found {len(pending)} trailing values."
                )

            star["blocks"][current_block]["loops"].append(
                {
                    "columns": columns,
                    "rows": rows,
                }
            )
            continue

        if stripped.startswith("_"):
            tokens = _split_star_line(raw)
            if len(tokens) < 2:
                raise ValueError(
                    f"STAR scalar item has no value in {filename}, line {i + 1}: {stripped}"
                )
            star["blocks"][current_block]["items"].append((tokens[0], tokens[1]))
            i += 1
            continue

        # Unknown non-empty syntax outside a loop. Keeping silent here would make
        # malformed input difficult to diagnose.
        raise ValueError(
            f"Unsupported or malformed STAR syntax in {filename}, line {i + 1}: {stripped}"
        )

    return star


def _quote_star_value(value):
    """Convert a value to a safe single-line STAR token."""
    text = str(value)
    if text == "":
        return "''"
    if any(char.isspace() for char in text) or text.startswith("#") or "'" in text or '"' in text:
        # Prefer single quotes; if needed, use double quotes. RELION paths almost
        # never contain both quote types.
        if "'" not in text:
            return f"'{text}'"
        if '"' not in text:
            return f'"{text}"'
        raise ValueError(f"Cannot safely write STAR token containing both quote types: {text!r}")
    return text


def write_star_text(star, filename):
    """Write the in-memory STAR representation in canonical RELION-style text."""
    with open(filename, "w", encoding="utf-8", newline="\n") as handle:
        preamble = star.get("preamble", [])
        for line in preamble:
            handle.write(line.rstrip("\n") + "\n")
        if preamble and preamble[-1].strip():
            handle.write("\n")

        for block_name, block in star["blocks"].items():
            handle.write(f"data_{block_name}\n\n")

            for label, value in block.get("items", []):
                handle.write(f"{label} {_quote_star_value(value)}\n")
            if block.get("items"):
                handle.write("\n")

            for loop in block.get("loops", []):
                columns = loop["columns"]
                rows = loop["rows"]
                handle.write("loop_\n")
                for column_number, label in enumerate(columns, start=1):
                    handle.write(f"{label} #{column_number}\n")
                for row in rows:
                    if len(row) != len(columns):
                        raise ValueError(
                            f"Cannot write data_{block_name}: row has {len(row)} values "
                            f"but table has {len(columns)} columns."
                        )
                    handle.write(" ".join(_quote_star_value(value) for value in row) + "\n")
                handle.write("\n")


def find_star_loop(star, block_name, required_labels):
    """Find a loop by block name, with a label-based fallback."""
    required = {_normalise_label(label) for label in required_labels}
    requested_block = _normalise_block_name(block_name)

    # Prefer the explicitly named block.
    for name, block in star["blocks"].items():
        if _normalise_block_name(name) != requested_block:
            continue
        for loop in block["loops"]:
            labels = {_normalise_label(label) for label in loop["columns"]}
            if required.issubset(labels):
                return loop

    # Fallback for unusual block names.
    for block in star["blocks"].values():
        for loop in block["loops"]:
            labels = {_normalise_label(label) for label in loop["columns"]}
            if required.issubset(labels):
                return loop

    missing = ", ".join(sorted(required_labels))
    raise KeyError(
        f"Could not find a STAR loop containing [{missing}] in data_{block_name}."
    )


def star_column_index(loop, label):
    wanted = _normalise_label(label)
    for index, existing_label in enumerate(loop["columns"]):
        if _normalise_label(existing_label) == wanted:
            return index
    raise KeyError(f"STAR column {label} was not found.")


def get_star_column(loop, label):
    index = star_column_index(loop, label)
    return [row[index] for row in loop["rows"]]


def set_star_column(loop, label, values):
    index = star_column_index(loop, label)
    values = list(values)
    if len(values) != len(loop["rows"]):
        raise ValueError(
            f"Cannot set {label}: got {len(values)} values for {len(loop['rows'])} rows."
        )
    for row, value in zip(loop["rows"], values):
        row[index] = str(value)


def set_star_column_constant(loop, label, value):
    index = star_column_index(loop, label)
    text = str(value)
    for row in loop["rows"]:
        row[index] = text


def translation_twoD_image(image, trans_X, trans_Y):
    # transX/Y are all in pixels. Ignore the decimal part.
    # image should be a NumPy array and in real space.
    # Crop the density outside after translation.
    trans_x = int(np.floor(trans_X + 0.5))
    trans_y = int(np.floor(trans_Y + 0.5))
    ysize, xsize = image.shape

    start_x = max(0, trans_x)
    end_x = xsize if trans_x >= 0 else xsize + trans_x
    start_y = max(0, trans_y)
    end_y = ysize if trans_y >= 0 else ysize + trans_y

    translated_image = np.zeros_like(image)
    translated_image[start_y:end_y, start_x:end_x] = image[
        max(0, -trans_y):ysize - max(0, trans_y),
        max(0, -trans_x):xsize - max(0, trans_x),
    ]

    return translated_image


def create_gridsearch_parser():
    parser = argparse.ArgumentParser(
        description="Crop block images from particle images. The star file should be the output of relion-BBR or relion-SIRM"
    )
    parser.add_argument("--star_name", type=str, required=True, help="Input star file")
    parser.add_argument(
        "--output_root_name",
        type=str,
        default="output",
        help="Output root name of star and stack files. Default = output. So every stack has name of output_000x.mrcs. And the output star has name output.star",
    )
    parser.add_argument("--newboxsize", type=int, default=128, help="The block boxsize in pixel. Default = 128")
    parser.add_argument(
        "--batchsize",
        type=int,
        default=5000,
        help="Number of sub-particles in one stack. Default = 5000. Split the output stacks in order to prevent from using too much RAM.",
    )
    parser.add_argument("--dohighpass", action="store_true", help="Do high pass filter to the output stacks. default = False")
    parser.add_argument("--highpassFreq", type=float, default=50.0, help="The high pass frequency in Angstrom. Default = 50.")
    parser.add_argument("--dowhitening", action="store_true", help="Do whitening filter to the output stacks. default = False")
    parser.add_argument("--doSkipShifting", action="store_true", help="Skip shifting the particles to their centers. default = False")
    parser.add_argument("--doOnlyMakeStar", action="store_true", help="Only generate the final starfile. default = False")
    return parser


def getSpectrum_divideBySpectrum(img):
    img_FFT = np.fft.fftshift(np.fft.fft2(img))
    xsize = img.shape[-1]
    ysize = img.shape[-2]
    center_Y, center_X = ysize // 2, xsize // 2
    j_coords, i_coords = np.meshgrid(np.arange(ysize), np.arange(xsize), indexing="ij")
    dist = np.round(np.sqrt((j_coords - center_Y) ** 2 + (i_coords - center_X) ** 2)).astype(int)
    max_radius = dist.max() + 1
    spectrum = np.bincount(dist.ravel(), weights=np.abs(img_FFT).ravel(), minlength=max_radius)
    count_freq = np.bincount(dist.ravel(), minlength=max_radius)
    with np.errstate(divide="ignore", invalid="ignore"):
        div_spec = np.ones_like(spectrum)
        nonzero = count_freq > 0
        div_spec[nonzero] = 1.0 / (spectrum[nonzero] / count_freq[nonzero])
    div_spec[0] = 1.0
    img_FFT *= div_spec[dist]
    img_IFT = np.fft.ifft2(np.fft.ifftshift(img_FFT)).real
    return img_IFT


def normalize(img):
    ysize, xsize = img.shape[-2], img.shape[-1]
    j_coords, i_coords = np.meshgrid(np.arange(ysize), np.arange(xsize), indexing="ij")
    points = np.vstack(
        [
            i_coords.ravel(),
            j_coords.ravel(),
            img.ravel(),
            np.ones_like(img).ravel(),
        ]
    )
    pA, pB, pC = fit_least_squares_plane(points)
    img = img - (pA * i_coords + pB * j_coords + pC)
    ave, std = calculateAvgStddev(img)
    if std > 0.0:
        img = (img - ave) / std
    return img


def fit_least_squares_plane(points):
    x = points[0, :]
    y = points[1, :]
    z = points[2, :]
    w = points[3, :]
    W2 = w * w

    D = np.sum(x * x * W2)
    E = np.sum(x * y * W2)
    F = np.sum(x * W2)
    G = np.sum(y * y * W2)
    H = np.sum(y * W2)
    I = np.sum(W2)
    J = np.sum(x * z * W2)
    K = np.sum(y * z * W2)
    L = np.sum(z * W2)

    denom = F * F * G - 2 * E * F * H + D * H * H + E * E * I - D * G * I

    plane_a = (H * H * J - G * I * J + E * I * K + F * G * L - H * (F * K + E * L)) / denom
    plane_b = (E * I * J + F * F * K - D * I * K + D * H * L - F * (H * J + E * L)) / denom
    plane_c = (F * G * J - E * H * J - E * F * K + D * H * K + E * E * L - D * G * L) / denom

    return plane_a, plane_b, plane_c


def calculateAvgStddev(img):
    SUM = np.sum(img)
    SUM2 = np.sum(img * img)
    n = float(img.shape[-1] * img.shape[-2])
    ave = SUM / n
    std = np.sqrt((SUM2 / n) - (ave * ave))
    return ave, std


def highpassfilter(img, high_pass, angpix):
    ori_size = img.shape[-2]
    FT = np.fft.fftshift(np.fft.fft2(img))
    filter_edge_width = 4
    ires_filter = round((ori_size * angpix) / high_pass)
    filter_edge_halfwidth = filter_edge_width / 2

    edge_low = max(0.0, (ires_filter - filter_edge_halfwidth) / ori_size)
    edge_high = min(FT.shape[-1], (ires_filter + filter_edge_halfwidth) / ori_size)
    edge_width = edge_high - edge_low

    H, W = FT.shape[-2], FT.shape[-1]
    y = np.arange(H) - H // 2
    x = np.arange(W) - W // 2
    yy, xx = np.meshgrid(y, x, indexing="ij")
    r = np.sqrt(xx**2 + yy**2) / ori_size

    mask = np.ones_like(FT, dtype=FT.dtype)
    mask[r < edge_low] = 0.0
    transition = (r >= edge_low) & (r <= edge_high)
    if edge_width > 0:
        mask[transition] *= 0.5 - 0.5 * np.cos(
            np.pi * (r[transition] - edge_low) / edge_width
        )

    FT *= mask
    img_IFT = np.fft.ifft2(np.fft.ifftshift(FT)).real
    return img_IFT


if __name__ == "__main__":
    parser = create_gridsearch_parser()
    args = parser.parse_args()
    star_name = args.star_name
    output_root_name = args.output_root_name + "_"
    crop_size = args.newboxsize
    batch_size = args.batchsize
    doSkipShifting = args.doSkipShifting
    dohighpass = args.dohighpass
    highpassFreq = args.highpassFreq
    doOnlyMakeStar = args.doOnlyMakeStar

    # Load the STAR file using the built-in text parser.
    star_data = read_star_text(star_name)
    particles_loop = find_star_loop(
        star_data,
        "particles",
        ["rlnOriginXAngst", "rlnOriginYAngst", "rlnImageName"],
    )
    optics_loop = find_star_loop(
        star_data,
        "optics",
        ["rlnImagePixelSize", "rlnImageSize"],
    )

    # Extract relevant columns.
    origin_x_angst = np.asarray(get_star_column(particles_loop, "rlnOriginXAngst"), dtype=np.float64)
    origin_y_angst = np.asarray(get_star_column(particles_loop, "rlnOriginYAngst"), dtype=np.float64)
    image_names = np.asarray(get_star_column(particles_loop, "rlnImageName"), dtype=object)

    optics_pixel_sizes = get_star_column(optics_loop, "rlnImagePixelSize")
    if not optics_pixel_sizes:
        raise ValueError("The data_optics table contains no rows.")
    pixel_size = float(optics_pixel_sizes[0])  # Same assumption as the original script.

    # Convert shifts from Angstrom to pixels.
    origin_x_pixels = origin_x_angst / pixel_size
    origin_y_pixels = origin_y_angst / pixel_size

    new_image_names = []
    valid_indices = []
    batch_index = 1
    batch_images = []
    h = -1
    w = -1
    whitening = args.dowhitening

    def save_current_batch():
        global batch_images, batch_index
        if len(batch_images) == 0:
            return
        new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
        cropped_stack = np.array(batch_images, dtype=np.float32)
        with mrcfile.new(new_mrc_filename, overwrite=True) as new_mrc:
            new_mrc.set_data(cropped_stack)
        print(f"Saved {new_mrc_filename} with {len(batch_images)} images.")
        batch_images = []
        batch_index += 1

    if not doOnlyMakeStar:
        for i, image_name in enumerate(image_names):
            try:
                index_text, mrc_filename = str(image_name).split("@", 1)
                index = int(index_text) - 1  # RELION indices start from 1.

                with mrcfile.mmap(mrc_filename, mode="r") as mrc:
                    image = np.asarray(mrc.data[index])

                if image is None or image.size == 0 or image.ndim != 2:
                    print(
                        f"Skip bad image: {image_name}, "
                        f"shape={getattr(image, 'shape', None)}"
                    )
                    continue

                if h < 0 and w < 0:
                    h, w = image.shape

                if not doSkipShifting:
                    shift_x, shift_y = origin_x_pixels[i], origin_y_pixels[i]
                    shifted_image = translation_twoD_image(image, shift_x, shift_y)
                    cropped_image = shifted_image
                    if crop_size > 0:
                        center_x, center_y = w // 2, h // 2
                        cropped_image = shifted_image[
                            center_y - crop_size // 2:center_y + crop_size // 2,
                            center_x - crop_size // 2:center_x + crop_size // 2,
                        ]
                else:
                    cropped_image = image
                    if crop_size > 0:
                        center_x, center_y = w // 2, h // 2
                        cropped_image = image[
                            center_y - crop_size // 2:center_y + crop_size // 2,
                            center_x - crop_size // 2:center_x + crop_size // 2,
                        ]

                if cropped_image is None or cropped_image.size == 0 or cropped_image.ndim != 2:
                    print(
                        f"Skip empty cropped image: {image_name}, "
                        f"shape={getattr(cropped_image, 'shape', None)}"
                    )
                    continue

                if whitening:
                    img_IFT = getSpectrum_divideBySpectrum(cropped_image)
                    cropped_image = normalize(img_IFT)
                if dohighpass:
                    cropped_image = highpassfilter(cropped_image, highpassFreq, pixel_size)

                batch_images.append(cropped_image)
                new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
                new_image_names.append(f"{len(batch_images)}@{new_mrc_filename}")
                valid_indices.append(i)

                if len(batch_images) == batch_size:
                    save_current_batch()

            except Exception as exc:
                print(f"Skip failed image: {image_name}, error: {exc}")
                continue

        save_current_batch()
    else:
        for i, _image_name in enumerate(image_names):
            batch_images.append(i)
            new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
            new_image_names.append(f"{len(batch_images)}@{new_mrc_filename}")
            if len(batch_images) == batch_size or i == len(image_names) - 1:
                batch_images = []
                batch_index += 1

    # Filter particle rows exactly as the former DataFrame iloc operation did.
    if not doOnlyMakeStar:
        particles_loop["rows"] = [particles_loop["rows"][i] for i in valid_indices]

    set_star_column(particles_loop, "rlnImageName", new_image_names)

    if not doSkipShifting:
        set_star_column_constant(particles_loop, "rlnOriginXAngst", "0.0")
        set_star_column_constant(particles_loop, "rlnOriginYAngst", "0.0")

    if crop_size > 0:
        set_star_column_constant(optics_loop, "rlnImageSize", str(crop_size))
    elif h > 0:
        set_star_column_constant(optics_loop, "rlnImageSize", str(h))
    # With --doOnlyMakeStar and newboxsize <= 0 there is no image read from which
    # to infer h, so retain the original rlnImageSize instead of writing -1.

    output_star_name = args.output_root_name + ".star"
    write_star_text(star_data, output_star_name)
    print("New STAR file saved as", output_star_name)
