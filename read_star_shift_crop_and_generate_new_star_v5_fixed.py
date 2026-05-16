import starfile
import mrcfile
import numpy as np
import os,argparse
# changelog v4
# Add normalization
# changelog v5
# Add highpass filter
def translation_twoD_image(image,trans_X,trans_Y):
	# transX/Y are all in pixels. Ingore the decimal part.
	# image should be cp array and in real space.
	# crop the density outside after trans.
	trans_x=int(np.floor(trans_X+0.5))
	trans_y=int(np.floor(trans_Y+0.5))
	ysize, xsize = image.shape

	# Determine the start and end indices for slicing
	start_x = max(0, trans_x)
	end_x = xsize if trans_x >= 0 else xsize + trans_x
	start_y = max(0, trans_y)
	end_y = ysize if trans_y >= 0 else ysize + trans_y

	# Initialize the translated image with zeros
	translated_image = np.zeros_like(image)

	# Fill the translated image with the appropriate slice of the original image
	translated_image[start_y:end_y, start_x:end_x] = image[max(0, -trans_y):ysize - max(0, trans_y), max(0, -trans_x):xsize - max(0, trans_x)]

	return translated_image
def create_gridsearch_parser():
	parser = argparse.ArgumentParser(description="Crop block images from particle images. The star file should be the output of relion-BBR or relion-SIRM")
	parser.add_argument("--star_name", type=str, required=True, help="Input star file")
	parser.add_argument("--output_root_name", type=str, default="output", help="Output root name of star and stack files. Default = output. So every stack has name of output_000x.mrcs. And the output star has name output.star")
	parser.add_argument("--newboxsize", type=int, default=128, help="The block boxsize in pixel. Default = 128")
	parser.add_argument("--batchsize", type=int, default=5000, help="Number of sub-particles in one stack. Default = 5000. Split the output stacks in order to prevent from using too much RAM.")
	parser.add_argument("--dohighpass", action='store_true', help="Do high pass filter to the output stacks. default = False")
	parser.add_argument("--highpassFreq", type=float, default=50., help="The high pass frequency in Angstrom. Default = 50.")
	parser.add_argument("--dowhitening", action='store_true', help="Do whitening filter to the output stacks. default = False")
	parser.add_argument("--doSkipShifting", action='store_true', help="Skip shifting the particles to their centers. default = False")
	parser.add_argument("--doOnlyMakeStar", action='store_true', help="Only generate the final starfile. default = False")
	return parser
def getSpectrum_divideBySpectrum(img):
	img_FFT = np.fft.fftshift(np.fft.fft2(img))
	xsize=img.shape[-1]
	ysize=img.shape[-2]
	center_Y, center_X = ysize // 2, xsize // 2
	j_coords, i_coords = np.meshgrid(np.arange(ysize), np.arange(xsize), indexing='ij')
	dist = np.round(np.sqrt((j_coords - center_Y)**2 + (i_coords - center_X)**2)).astype(int)
	max_radius = dist.max() + 1
	spectrum = np.bincount(dist.ravel(), weights=np.abs(img_FFT).ravel(), minlength=max_radius)
	count_freq = np.bincount(dist.ravel(), minlength=max_radius)
	with np.errstate(divide='ignore', invalid='ignore'):
		div_spec = np.ones_like(spectrum)
		nonzero = count_freq > 0
		div_spec[nonzero] = 1.0 / (spectrum[nonzero] / count_freq[nonzero])
	div_spec[0] = 1.0
	img_FFT *= div_spec[dist]
	img_IFT = np.fft.ifft2(np.fft.ifftshift(img_FFT)).real
	return img_IFT

def normalize(img):
	ysize, xsize = img.shape[-2], img.shape[-1]
	j_coords, i_coords = np.meshgrid(np.arange(ysize), np.arange(xsize), indexing='ij')
	points = np.vstack([
		i_coords.ravel(),
		j_coords.ravel(),
		img.ravel(),
		np.ones_like(img).ravel()
	])
	pA, pB, pC = fit_least_squares_plane(points)
	img = img - (pA * i_coords + pB * j_coords + pC)
	ave, std = calculateAvgStddev(img)
	if std > 0.0:
		img = (img - ave) / std
	return img
def fit_least_squares_plane(points):
    x = points[0,:]
    y = points[1,:]
    z = points[2,:]
    w = points[3,:]
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
	SUM2 = np.sum(img*img)
	n = float(img.shape[-1]*img.shape[-2])
	ave = SUM / n
	std = np.sqrt((SUM2 / n) - (ave * ave))
	return ave,std
def highpassfilter(img, high_pass, angpix):
	ori_size = img.shape[-2]
	FT = np.fft.fftshift(np.fft.fft2(img))
	filter_edge_width = 4
	ires_filter = round((ori_size * angpix) / high_pass)
	filter_edge_halfwidth = filter_edge_width / 2

	edge_low = max(0., (ires_filter - filter_edge_halfwidth) / ori_size)
	edge_high = min(FT.shape[-1], (ires_filter + filter_edge_halfwidth) / ori_size)
	edge_width = edge_high - edge_low

	# Create coordinate grid centered at the center of the array
	H, W = FT.shape[-2], FT.shape[-1]
	y = np.arange(H) - H // 2
	x = np.arange(W) - W // 2
	yy, xx = np.meshgrid(y, x, indexing='ij')
	r = np.sqrt(xx**2 + yy**2) / ori_size  # normalized radius

	# Build the filter mask
	mask = np.ones_like(FT, dtype=FT.dtype)
	mask[r < edge_low] = 0.
	transition = (r >= edge_low) & (r <= edge_high)
	mask[transition] *= 0.5 - 0.5 * np.cos(np.pi * (r[transition] - edge_low) / edge_width)

    # Apply the mask
	FT *= mask
	img_IFT = np.fft.ifft2(np.fft.ifftshift(FT)).real
	return img_IFT
if __name__ == "__main__":
	parser = create_gridsearch_parser()
	args = parser.parse_args()
	star_name = args.star_name
	output_root_name = args.output_root_name+"_"
	crop_size = args.newboxsize
	batch_size = args.batchsize
	doSkipShifting = args.doSkipShifting
	dohighpass=args.dohighpass
	highpassFreq = args.highpassFreq
	doOnlyMakeStar = args.doOnlyMakeStar
	
	# Load the .star file
	star_data = starfile.read(star_name)
	
	# Extract relevant columns
	origin_x_angst = star_data["particles"]["rlnOriginXAngst"].to_numpy()
	origin_y_angst = star_data["particles"]["rlnOriginYAngst"].to_numpy()
	image_names = star_data["particles"]["rlnImageName"].to_numpy()
	pixel_size = star_data["optics"]["rlnImagePixelSize"].iloc[0]  # Assuming same pixel size for all images

	# Convert shifts from Ångström to integer pixels
	origin_x_pixels = (origin_x_angst / pixel_size)
	origin_y_pixels = (origin_y_angst / pixel_size)
	
	num_batches = (len(image_names) + batch_size - 1) // batch_size  # Compute total batches

	# Prepare new STAR file data
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

	if(not doOnlyMakeStar):
		for i, image_name in enumerate(image_names):
			try:
				# Extract the MRC file name and particle index
				index, mrc_filename = image_name.split('@')
				index = int(index) - 1  # RELION indices start from 1

				# Open the corresponding MRC file
				with mrcfile.mmap(mrc_filename, mode='r') as mrc:
					image = np.asarray(mrc.data[index])

				# Skip empty or invalid images
				if image is None or image.size == 0 or image.ndim != 2:
					print(f"Skip bad image: {image_name}, shape={getattr(image, 'shape', None)}")
					continue

				# Get image dimensions from the first valid image
				if(h < 0 and w < 0):
					h, w = image.shape

				if(not doSkipShifting):
					# Compute valid region after shifting
					shift_x, shift_y = origin_x_pixels[i], origin_y_pixels[i]
					shifted_image = translation_twoD_image(image, shift_x, shift_y)
					cropped_image = shifted_image
					if(crop_size > 0):
						# Crop the image
						center_x, center_y = w // 2, h // 2
						cropped_image = shifted_image[
							center_y - crop_size // 2 : center_y + crop_size // 2,
							center_x - crop_size // 2 : center_x + crop_size // 2,
						]
				else:
					cropped_image = image
					if(crop_size > 0):
						# Crop the image
						center_x, center_y = w // 2, h // 2
						cropped_image = image[
							center_y - crop_size // 2 : center_y + crop_size // 2,
							center_x - crop_size // 2 : center_x + crop_size // 2,
						]

				# Skip empty crop results. This can happen if crop_size is larger than the image,
				# or if the crop window is outside the available array.
				if cropped_image is None or cropped_image.size == 0 or cropped_image.ndim != 2:
					print(f"Skip empty cropped image: {image_name}, shape={getattr(cropped_image, 'shape', None)}")
					continue

				if(whitening):
					img_IFT = getSpectrum_divideBySpectrum(cropped_image)
					cropped_image = normalize(img_IFT)
				if(dohighpass):
					tmp_img = highpassfilter(cropped_image, highpassFreq, pixel_size)
					cropped_image = tmp_img

				batch_images.append(cropped_image)
				new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
				new_image_names.append(f"{len(batch_images)}@{new_mrc_filename}")
				valid_indices.append(i)

				# Save when batch reaches batch_size. The remaining images are saved after the loop.
				if len(batch_images) == batch_size:
					save_current_batch()

			except Exception as e:
				print(f"Skip failed image: {image_name}, error: {e}")
				continue

		# Save the final incomplete batch, even if the last input image failed.
		save_current_batch()
	else:
		for i, image_name in enumerate(image_names):
			batch_images.append(i)
			new_mrc_filename = f"{output_root_name}{batch_index:04d}.mrcs"
			new_image_names.append(f"{len(batch_images)}@{new_mrc_filename}")
			if len(batch_images) == batch_size or i == len(image_names) - 1:
				batch_images = []  # Reset batch list
				batch_index += 1  # Increment batch index
	# Create a new .star file with updated entries
	new_star_data = star_data.copy()
	if(not doOnlyMakeStar):
		new_star_data["particles"] = star_data["particles"].iloc[valid_indices].copy()
	else:
		new_star_data["particles"] = star_data["particles"].copy()
	new_star_data["particles"]["rlnImageName"] = new_image_names
	if(not doSkipShifting):
		new_star_data["particles"]["rlnOriginXAngst"] = 0.0
		new_star_data["particles"]["rlnOriginYAngst"] = 0.0
	if(crop_size > 0):
		new_star_data["optics"]["rlnImageSize"] = crop_size
	else:
		new_star_data["optics"]["rlnImageSize"] = h
	# Save the new .star file
	starfile.write(new_star_data, args.output_root_name+".star", overwrite=True)

	print("New STAR file saved as ",args.output_root_name+".star")
