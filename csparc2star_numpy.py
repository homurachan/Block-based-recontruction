#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone CryoSPARC .cs -> RELION .star converter.

Runtime dependencies:
    - Python 3.8+
    - NumPy

This is a clean single-file extraction/reimplementation of the particle
conversion path used by pyem's csparc2star.py and metadata/cryosparc2.py.
It intentionally does not import pandas, scipy, starfile, or pyem.

License: GPL-3.0-or-later
Original pyem project and conventions:
    Copyright (C) Daniel Asarnow and pyem contributors
    https://github.com/asarnow/pyem

Implemented:
    * CryoSPARC v2+ structured .cs files
    * One primary .cs plus any number of passthrough .cs files, merged by uid
    * 3D refinement, multi-class 3D, and 2D alignment metadata
    * CTF, particle paths/indices, coordinates, helical IDs, shifts, poses
    * RELION 3.1+ optics-table output (default) and RELION 2 output
    * Class filtering, min posterior filtering, flip-Y operations
    * Path rewriting, UID-prefix stripping, simple coordinate STAR merging
    * Optional 3x3/3x4 particle transform

Not implemented:
    * CryoSPARC 0.6.5 CSV input
    * --movies trajectory export

Typical usage:
    python csparc2star_numpy.py particles.cs passthrough_particles.cs output.star
    python csparc2star_numpy.py particles.cs output.star --relion2
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import math
import os
import re
import shlex
import sys
from collections import OrderedDict
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Tuple

import numpy as np


VERSION = "1.0.0"
UID_PREFIX_RE = re.compile(r"[0-9]{21}_")

# Internal-only column names. They are never written to STAR.
UID = "__uid"
IMAGE_PATH = "__image_path"
IMAGE_INDEX = "__image_index"

# RELION field names used by the converter.
R = {
    "IMAGE_NAME": "rlnImageName",
    "IMAGE_ORIGINAL_NAME": "rlnImageOriginalName",
    "MICROGRAPH_NAME": "rlnMicrographName",
    "COORDX": "rlnCoordinateX",
    "COORDY": "rlnCoordinateY",
    "COORDZ": "rlnCoordinateZ",
    "ORIGINX": "rlnOriginX",
    "ORIGINY": "rlnOriginY",
    "ORIGINZ": "rlnOriginZ",
    "ORIGINXANGST": "rlnOriginXAngst",
    "ORIGINYANGST": "rlnOriginYAngst",
    "ORIGINZANGST": "rlnOriginZAngst",
    "ANGLEROT": "rlnAngleRot",
    "ANGLETILT": "rlnAngleTilt",
    "ANGLEPSI": "rlnAnglePsi",
    "ANGLEPSIPRIOR": "rlnAnglePsiPrior",
    "CLASS": "rlnClassNumber",
    "DEFOCUSU": "rlnDefocusU",
    "DEFOCUSV": "rlnDefocusV",
    "DEFOCUSANGLE": "rlnDefocusAngle",
    "PHASESHIFT": "rlnPhaseShift",
    "CS": "rlnSphericalAberration",
    "AC": "rlnAmplitudeContrast",
    "VOLTAGE": "rlnVoltage",
    "MAGNIFICATION": "rlnMagnification",
    "DETECTORPIXELSIZE": "rlnDetectorPixelSize",
    "BEAMTILTX": "rlnBeamTiltX",
    "BEAMTILTY": "rlnBeamTiltY",
    "CTFBFACTOR": "rlnCtfBfactor",
    "CTFMAXRESOLUTION": "rlnCtfMaxResolution",
    "CTFFIGUREOFMERIT": "rlnCtfFigureOfMerit",
    "RANDOMSUBSET": "rlnRandomSubset",
    "OPTICSGROUP": "rlnOpticsGroup",
    "OPTICSGROUPNAME": "rlnOpticsGroupName",
    "IMAGEPIXELSIZE": "rlnImagePixelSize",
    "IMAGESIZE": "rlnImageSize",
    "IMAGEDIMENSION": "rlnImageDimensionality",
    "MICROGRAPHPIXELSIZE": "rlnMicrographPixelSize",
    "HELICALTUBEID": "rlnHelicalTubeID",
    "MAGMAT00": "rlnMagMat00",
    "MAGMAT01": "rlnMagMat01",
    "MAGMAT10": "rlnMagMat10",
    "MAGMAT11": "rlnMagMat11",
}

ANGLE_FIELDS = [R["ANGLEROT"], R["ANGLETILT"], R["ANGLEPSI"]]
ORIGIN_FIELDS = [R["ORIGINX"], R["ORIGINY"], R["ORIGINZ"]]
ORIGIN_ANGST_FIELDS = [R["ORIGINXANGST"], R["ORIGINYANGST"], R["ORIGINZANGST"]]
COORD_FIELDS = [R["COORDX"], R["COORDY"], R["COORDZ"]]

OPTICS_FIELDS = [
    R["OPTICSGROUPNAME"], R["OPTICSGROUP"], R["IMAGEPIXELSIZE"],
    R["IMAGESIZE"], R["IMAGEDIMENSION"], R["MICROGRAPHPIXELSIZE"],
    R["VOLTAGE"], R["CS"], R["AC"], R["BEAMTILTX"], R["BEAMTILTY"],
    R["MAGMAT00"], R["MAGMAT01"], R["MAGMAT10"], R["MAGMAT11"],
]

FIELD_ORDER = [
    R["IMAGE_NAME"], R["IMAGE_ORIGINAL_NAME"], R["MICROGRAPH_NAME"],
    R["COORDX"], R["COORDY"], R["COORDZ"],
    R["ORIGINXANGST"], R["ORIGINYANGST"], R["ORIGINZANGST"],
    R["ORIGINX"], R["ORIGINY"], R["ORIGINZ"],
    R["ANGLEROT"], R["ANGLETILT"], R["ANGLEPSI"], R["ANGLEPSIPRIOR"],
    R["CLASS"], R["RANDOMSUBSET"], R["OPTICSGROUP"],
    R["DEFOCUSU"], R["DEFOCUSV"], R["DEFOCUSANGLE"], R["PHASESHIFT"],
    R["CTFMAXRESOLUTION"], R["CTFFIGUREOFMERIT"], R["CTFBFACTOR"],
    R["VOLTAGE"], R["CS"], R["AC"],
    R["MAGNIFICATION"], R["DETECTORPIXELSIZE"],
    R["IMAGEPIXELSIZE"], R["IMAGESIZE"], R["IMAGEDIMENSION"],
    R["MICROGRAPHPIXELSIZE"], R["HELICALTUBEID"],
    R["BEAMTILTX"], R["BEAMTILTY"],
    R["MAGMAT00"], R["MAGMAT01"], R["MAGMAT10"], R["MAGMAT11"],
    R["OPTICSGROUPNAME"],
]


class ColumnTable:
    """A minimal NumPy-backed table with one 1-D array per column."""

    def __init__(self, nrows: int = 0) -> None:
        self.nrows = int(nrows)
        self.columns: "OrderedDict[str, np.ndarray]" = OrderedDict()

    def __contains__(self, name: str) -> bool:
        return name in self.columns

    def __getitem__(self, name: str) -> np.ndarray:
        return self.columns[name]

    def __setitem__(self, name: str, values: object) -> None:
        arr = np.asarray(values)
        if arr.ndim == 0:
            arr = np.full(self.nrows, arr.item())
        if arr.ndim != 1:
            raise ValueError(f"Column {name!r} must be 1-D, got shape {arr.shape}")
        if self.nrows == 0:
            self.nrows = arr.shape[0]
        if arr.shape[0] != self.nrows:
            raise ValueError(
                f"Column {name!r} has {arr.shape[0]} rows, expected {self.nrows}"
            )
        self.columns[name] = arr

    def get(self, name: str, default: Optional[np.ndarray] = None) -> Optional[np.ndarray]:
        return self.columns.get(name, default)

    def pop(self, name: str) -> Optional[np.ndarray]:
        return self.columns.pop(name, None)

    def subset(self, selector: np.ndarray) -> "ColumnTable":
        selector = np.asarray(selector)
        out = ColumnTable(int(np.count_nonzero(selector)) if selector.dtype == bool else len(selector))
        for name, arr in self.columns.items():
            out[name] = arr[selector]
        return out

    def copy(self) -> "ColumnTable":
        out = ColumnTable(self.nrows)
        for name, arr in self.columns.items():
            out[name] = arr.copy()
        return out

    def public_columns(self) -> List[str]:
        return [name for name in self.columns if not name.startswith("__")]


# -------------------------- Generic NumPy helpers --------------------------


def load_cs(path: str, max_header_size: int, allow_pickle: bool) -> np.ndarray:
    kwargs = dict(allow_pickle=allow_pickle)
    try:
        arr = np.load(path, max_header_size=max_header_size, **kwargs)
    except TypeError:
        arr = np.load(path, **kwargs)
    if not isinstance(arr, np.ndarray) or arr.dtype.names is None:
        raise ValueError(f"{path}: expected a structured NumPy array (.cs file)")
    return arr


def has_field(cs: np.ndarray, name: str) -> bool:
    return cs.dtype.names is not None and name in cs.dtype.names


def decode_strings(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values)
    if values.dtype.kind == "U":
        return values.astype(object, copy=False)
    if values.dtype.kind == "S":
        return np.array([x.decode("utf-8", errors="replace") for x in values], dtype=object)
    if values.dtype.kind == "O":
        out = []
        for x in values:
            if isinstance(x, (bytes, np.bytes_)):
                out.append(bytes(x).decode("utf-8", errors="replace"))
            else:
                out.append(str(x))
        return np.array(out, dtype=object)
    return values


def clean_path_array(values: np.ndarray) -> np.ndarray:
    strings = decode_strings(values)
    return np.array([s[1:] if isinstance(s, str) and s.startswith(">") else s for s in strings], dtype=object)


def strip_uid_prefixes(values: np.ndarray, count: int = -1) -> np.ndarray:
    values = clean_path_array(values)
    if count == 0:
        return values
    return np.array([UID_PREFIX_RE.sub("", str(v), count=count) for v in values], dtype=object)


def replace_directory(values: np.ndarray, directory: str) -> np.ndarray:
    values = clean_path_array(values)
    return np.array([os.path.join(directory, os.path.basename(str(v))) for v in values], dtype=object)


def assign_vector(table: ColumnTable, names: Sequence[str], values: np.ndarray) -> None:
    arr = np.asarray(values)
    if arr.ndim == 1:
        if len(names) != 1:
            raise ValueError(f"Expected vector with {len(names)} columns, got 1-D values")
        table[names[0]] = arr
        return
    if arr.ndim != 2:
        raise ValueError(f"Expected a 2-D vector field, got shape {arr.shape}")
    for j in range(min(arr.shape[1], len(names))):
        table[names[j]] = arr[:, j]


def map_first_available(
    cs: np.ndarray,
    table: ColumnTable,
    output_name: str,
    input_names: Sequence[str],
    *,
    strings: bool = False,
) -> None:
    if output_name in table:
        return
    for name in input_names:
        if has_field(cs, name):
            values = cs[name]
            table[output_name] = clean_path_array(values) if strings else values
            return


def merge_tables_by_uid(primary: ColumnTable, auxiliary: ColumnTable, log: logging.Logger) -> None:
    new_fields = [name for name in auxiliary.columns if name not in primary.columns and name != UID]
    if not new_fields:
        return

    if UID in primary and UID in auxiliary:
        left_uid = np.asarray(primary[UID])
        right_uid = np.asarray(auxiliary[UID])
        order = np.argsort(right_uid, kind="mergesort")
        sorted_uid = right_uid[order]
        pos = np.searchsorted(sorted_uid, left_uid)
        valid = pos < sorted_uid.size
        valid_idx = np.flatnonzero(valid)
        if valid_idx.size:
            valid[valid_idx] &= sorted_uid[pos[valid_idx]] == left_uid[valid_idx]
        matched = int(valid.sum())
        if matched != primary.nrows:
            log.warning(
                "UID merge matched %d / %d primary rows", matched, primary.nrows
            )
        src = np.zeros(primary.nrows, dtype=np.int64)
        src[valid] = order[pos[valid]]
        for name in new_fields:
            arr = auxiliary[name]
            if valid.all():
                primary[name] = arr[src]
            else:
                if arr.dtype.kind in "iu":
                    out = np.zeros(primary.nrows, dtype=arr.dtype)
                elif arr.dtype.kind in "fc":
                    out = np.full(primary.nrows, np.nan, dtype=arr.dtype)
                else:
                    out = np.full(primary.nrows, "", dtype=object)
                out[valid] = arr[src[valid]]
                primary[name] = out
        return

    if primary.nrows == auxiliary.nrows:
        log.warning("No uid field available; merging passthrough columns by row order")
        for name in new_fields:
            primary[name] = auxiliary[name]
        return

    raise ValueError(
        "Cannot merge passthrough file: no common uid field and row counts differ "
        f"({primary.nrows} vs {auxiliary.nrows})"
    )


# -------------------------- Rotation conversions --------------------------


def expmap_batch(e: np.ndarray) -> np.ndarray:
    """pyem-compatible exponential-map vectors -> rotation matrices."""
    e = np.asarray(e, dtype=np.float64)
    if e.ndim != 2 or e.shape[1] != 3:
        raise ValueError(f"Pose array must have shape (N,3), got {e.shape}")
    n = e.shape[0]
    theta = np.linalg.norm(e, axis=1)
    r = np.broadcast_to(np.eye(3, dtype=np.float64), (n, 3, 3)).copy()
    nz = theta >= 1e-16
    if not np.any(nz):
        return r
    w = e[nz] / theta[nz, None]
    k = np.zeros((w.shape[0], 3, 3), dtype=np.float64)
    # This sign convention deliberately matches pyem.geom.expmap.
    k[:, 0, 1] = w[:, 2]
    k[:, 0, 2] = -w[:, 1]
    k[:, 1, 0] = -w[:, 2]
    k[:, 1, 2] = w[:, 0]
    k[:, 2, 0] = w[:, 1]
    k[:, 2, 1] = -w[:, 0]
    k2 = np.matmul(k, k)
    s = np.sin(theta[nz])[:, None, None]
    c = (1.0 - np.cos(theta[nz]))[:, None, None]
    r[nz] += s * k + c * k2
    return r


def rot_to_euler_batch(r: np.ndarray) -> np.ndarray:
    """Rotation matrices -> RELION-compatible (rot, tilt, psi), radians."""
    r = np.asarray(r, dtype=np.float64)
    if r.ndim == 2:
        r = r[None, :, :]
    if r.ndim != 3 or r.shape[1:] != (3, 3):
        raise ValueError(f"Rotation matrix array must have shape (N,3,3), got {r.shape}")
    eps = np.finfo(np.float64).eps
    abs_sb = np.sqrt(r[:, 0, 2] ** 2 + r[:, 1, 2] ** 2)
    regular = abs_sb > 16 * eps
    alpha = np.zeros(r.shape[0], dtype=np.float64)
    beta = np.zeros(r.shape[0], dtype=np.float64)
    gamma = np.zeros(r.shape[0], dtype=np.float64)

    if np.any(regular):
        rr = r[regular]
        g = np.arctan2(rr[:, 1, 2], -rr[:, 0, 2])
        a = np.arctan2(rr[:, 2, 1], rr[:, 2, 0])
        sing = np.abs(np.sin(g)) < eps
        sign_sb = np.empty(g.shape[0], dtype=np.float64)
        if np.any(sing):
            sign_sb[sing] = np.sign(-rr[sing, 0, 2]) / np.cos(g[sing])
        if np.any(~sing):
            sg = np.sin(g[~sing])
            sign_sb[~sing] = np.where(
                sg > 0,
                np.sign(rr[~sing, 1, 2]),
                -np.sign(rr[~sing, 1, 2]),
            )
        b = np.arctan2(sign_sb * abs_sb[regular], rr[:, 2, 2])
        alpha[regular], beta[regular], gamma[regular] = a, b, g

    if np.any(~regular):
        rr = r[~regular]
        positive = np.sign(rr[:, 2, 2]) > 0
        b = np.where(positive, 0.0, np.pi)
        g = np.where(
            positive,
            np.arctan2(-rr[:, 1, 0], rr[:, 0, 0]),
            np.arctan2(rr[:, 1, 0], -rr[:, 0, 0]),
        )
        beta[~regular], gamma[~regular] = b, g

    return np.column_stack((alpha, beta, gamma))


def euler_to_rot_batch(eulers_rad: np.ndarray) -> np.ndarray:
    e = np.asarray(eulers_rad, dtype=np.float64)
    if e.ndim != 2 or e.shape[1] != 3:
        raise ValueError(f"Euler array must have shape (N,3), got {e.shape}")
    a, b, g = e[:, 0], e[:, 1], e[:, 2]
    ca, cb, cg = np.cos(a), np.cos(b), np.cos(g)
    sa, sb, sg = np.sin(a), np.sin(b), np.sin(g)
    cc, cs = cb * ca, cb * sa
    sc, ss = sb * ca, sb * sa
    r = np.empty((e.shape[0], 3, 3), dtype=np.float64)
    r[:, 0, 0] = cg * cc - sg * sa
    r[:, 0, 1] = cg * cs + sg * ca
    r[:, 0, 2] = -cg * sb
    r[:, 1, 0] = -sg * cc - cg * sa
    r[:, 1, 1] = -sg * cs + cg * ca
    r[:, 1, 2] = sg * sb
    r[:, 2, 0] = sc
    r[:, 2, 1] = ss
    r[:, 2, 2] = cb
    return r


def table_has_3d_angles(table: ColumnTable) -> bool:
    return all(name in table for name in ANGLE_FIELDS)


def apply_transform(
    table: ColumnTable,
    matrix: np.ndarray,
    *,
    leftmult: bool = False,
    log: Optional[logging.Logger] = None,
) -> None:
    matrix = np.asarray(matrix, dtype=np.float64)
    translation = None
    if matrix.shape == (3, 4):
        translation = matrix[:, 3].copy()
        matrix = matrix[:, :3]
    if matrix.shape != (3, 3):
        raise ValueError("Transform must be a 3x3 rotation or 3x4 rotation+translation matrix")

    if not table_has_3d_angles(table):
        if log:
            log.warning("Skipping 3-D transform because full Euler angles are absent")
        return

    eulers = np.column_stack([table[name] for name in ANGLE_FIELDS])
    rots = euler_to_rot_batch(np.deg2rad(eulers))
    if leftmult:
        # Matches pyem.star.transform_star(..., leftmult=True).
        new_rots = np.transpose(
            np.matmul(np.transpose(rots, (0, 2, 1)), matrix), (0, 2, 1)
        ).copy()
    else:
        new_rots = np.matmul(rots, matrix)
    new_eulers = np.rad2deg(rot_to_euler_batch(new_rots))
    for j, name in enumerate(ANGLE_FIELDS):
        table[name] = new_eulers[:, j]

    if translation is not None and np.linalg.norm(translation) > 0:
        shifts = np.matmul(new_rots, translation)
        for j, name in enumerate(ORIGIN_FIELDS):
            if name in table:
                table[name] = np.asarray(table[name], dtype=np.float64) + shifts[:, j]


# -------------------------- CryoSPARC extraction --------------------------


def extract_common(cs: np.ndarray, *, include_model: bool, minphic: float, log: logging.Logger) -> Tuple[ColumnTable, np.ndarray]:
    table = ColumnTable(cs.shape[0])

    if has_field(cs, "uid"):
        table[UID] = cs["uid"]

    map_first_available(cs, table, R["VOLTAGE"], ["ctf/accel_kv", "mscope_params/accel_kv"])
    map_first_available(cs, table, R["IMAGEPIXELSIZE"], ["blob/psize_A"])
    map_first_available(cs, table, R["MICROGRAPHPIXELSIZE"], ["micrograph_blob/psize_A"])
    map_first_available(cs, table, R["AC"], ["ctf/amp_contrast", "ctf/ac"])
    map_first_available(cs, table, R["CS"], ["ctf/cs_mm", "mscope_params/cs_mm"])
    map_first_available(cs, table, R["DEFOCUSU"], ["ctf/df1_A"])
    map_first_available(cs, table, R["DEFOCUSV"], ["ctf/df2_A"])
    map_first_available(cs, table, R["DEFOCUSANGLE"], ["ctf/df_angle_rad"])
    map_first_available(cs, table, R["PHASESHIFT"], ["ctf/phase_shift_rad"])
    map_first_available(cs, table, R["CTFFIGUREOFMERIT"], ["ctf/cross_corr_ctffind4"])
    map_first_available(cs, table, R["CTFMAXRESOLUTION"], ["ctf/ctf_fit_to_A"])
    map_first_available(cs, table, R["CTFBFACTOR"], ["ctf/bfactor"])
    map_first_available(cs, table, R["OPTICSGROUP"], ["ctf/exp_group_id"])
    map_first_available(cs, table, IMAGE_PATH, ["blob/path"], strings=True)
    map_first_available(cs, table, IMAGE_INDEX, ["blob/idx"])
    map_first_available(cs, table, R["MICROGRAPH_NAME"], ["location/micrograph_path", "micrograph_blob/path"], strings=True)
    map_first_available(cs, table, R["HELICALTUBEID"], ["filament/filament_uid"])

    # Normalized particle coordinates -> absolute pixels.
    if has_field(cs, "location/center_x_frac") and has_field(cs, "location/center_y_frac"):
        x = np.asarray(cs["location/center_x_frac"], dtype=np.float64).copy()
        y = np.asarray(cs["location/center_y_frac"], dtype=np.float64).copy()
        # The actual axis/inversion operations are applied later, because they are CLI-controlled.
        table["__coord_x_frac"] = x
        table["__coord_y_frac"] = y
        if has_field(cs, "location/micrograph_shape"):
            shape = np.asarray(cs["location/micrograph_shape"])
            if shape.ndim == 2 and shape.shape[1] >= 2:
                table["__micrograph_shape_y"] = shape[:, 0]
                table["__micrograph_shape_x"] = shape[:, 1]

    if has_field(cs, "blob/shape"):
        shape = np.asarray(cs["blob/shape"])
        if shape.ndim >= 2:
            table[R["IMAGESIZE"]] = shape[:, 0]

    if has_field(cs, "ctf/tilt_A") and has_field(cs, "ctf/cs_mm"):
        tilt = np.asarray(cs["ctf/tilt_A"], dtype=np.float64)
        cs_mm = np.asarray(cs["ctf/cs_mm"], dtype=np.float64)
        if tilt.ndim == 2 and tilt.shape[1] >= 2:
            table[R["BEAMTILTX"]] = np.arcsin(tilt[:, 0] / cs_mm * 1e-7) * 1e3
            table[R["BEAMTILTY"]] = np.arcsin(tilt[:, 1] / cs_mm * 1e-7) * 1e3

    if has_field(cs, "ctf/anisomag"):
        mag = np.asarray(cs["ctf/anisomag"])
        if mag.ndim == 2 and mag.shape[1] >= 4:
            table[R["MAGMAT00"]] = mag[:, 0]
            table[R["MAGMAT01"]] = mag[:, 1]
            table[R["MAGMAT10"]] = mag[:, 2]
            table[R["MAGMAT11"]] = mag[:, 3]

    if has_field(cs, "filament/filament_pose"):
        table[R["ANGLEPSIPRIOR"]] = np.rad2deg(-np.asarray(cs["filament/filament_pose"]) + np.pi / 2)

    keep = np.ones(cs.shape[0], dtype=bool)
    if include_model:
        keep &= extract_model(cs, table, minphic=minphic, log=log)

    return table, keep


def extract_model(cs: np.ndarray, table: ColumnTable, *, minphic: float, log: logging.Logger) -> np.ndarray:
    names = set(cs.dtype.names or ())
    keep = np.ones(cs.shape[0], dtype=bool)

    def assign_model(prefix: str, row_class: Optional[np.ndarray] = None) -> None:
        def selected(field: str) -> Optional[np.ndarray]:
            name = f"{prefix}/{field}"
            if name not in names:
                return None
            arr = np.asarray(cs[name])
            if row_class is None:
                return arr
            if field == "split" and arr.ndim == 1:
                return arr
            if arr.ndim >= 2 and arr.shape[1] > int(np.max(row_class, initial=0)):
                return arr[np.arange(arr.shape[0]), row_class, ...]
            return arr

        split = selected("split")
        shift = selected("shift")
        pose = selected("pose")
        cls = selected("class")
        if split is not None:
            table[R["RANDOMSUBSET"]] = np.asarray(split).reshape(-1)
        if shift is not None:
            assign_vector(table, ORIGIN_FIELDS, np.asarray(shift))
        if pose is not None:
            pose_arr = np.asarray(pose)
            if pose_arr.ndim == 2 and pose_arr.shape[1] == 3:
                eulers = np.rad2deg(rot_to_euler_batch(expmap_batch(pose_arr)))
                for j, field in enumerate(ANGLE_FIELDS):
                    table[field] = eulers[:, j]
            elif pose_arr.ndim == 1:
                table[R["ANGLEPSI"]] = np.rad2deg(pose_arr)
        if cls is not None:
            table[R["CLASS"]] = np.asarray(cls).reshape(-1)
        elif row_class is not None:
            table[R["CLASS"]] = row_class

    if "alignments3D/class_posterior" in names:
        log.info("Assigning pose from single 3-D refinement")
        assign_model("alignments3D")
        # Match pyem: --minphic is used for choosing among multiple 3-D
        # classes, not for filtering a single-refinement result.
        return keep

    if "alignments3D_multi/class_posterior" in names:
        log.info("Assigning pose from most likely alignments3D_multi class")
        posterior = np.asarray(cs["alignments3D_multi/class_posterior"])
        if posterior.ndim != 2:
            raise ValueError("alignments3D_multi/class_posterior must be a 2-D array")
        cls = np.argmax(posterior, axis=1)
        prob = posterior[np.arange(posterior.shape[0]), cls]
        assign_model("alignments3D_multi", cls)
        if minphic > 0:
            keep &= prob >= minphic
        return keep

    old_phic = [
        n for n in (cs.dtype.names or ())
        if n.endswith("/class_posterior") and "alignments3D" in n and "alignments2D" not in n
    ]
    if len(old_phic) > 1:
        log.info("Assigning pose from most likely legacy multi-class 3-D alignment")
        posterior = np.stack([np.asarray(cs[n]).reshape(-1) for n in old_phic], axis=1)
        cls = np.argmax(posterior, axis=1)
        prob = posterior[np.arange(posterior.shape[0]), cls]
        prefixes = [n.rsplit("/", 1)[0] for n in old_phic]

        def select_legacy(field: str) -> Optional[np.ndarray]:
            candidates = [f"{p}/{field}" for p in prefixes]
            if not all(name in names for name in candidates):
                return None
            arrays = [np.asarray(cs[name]) for name in candidates]
            return np.array([arrays[c][i] for i, c in enumerate(cls)])

        split = select_legacy("split")
        shift = select_legacy("shift")
        pose = select_legacy("pose")
        class_values = select_legacy("class")
        if split is not None:
            table[R["RANDOMSUBSET"]] = np.asarray(split).reshape(-1)
        if shift is not None:
            assign_vector(table, ORIGIN_FIELDS, np.asarray(shift))
        if pose is not None:
            pose_arr = np.asarray(pose)
            if pose_arr.ndim == 2 and pose_arr.shape[1] == 3:
                eulers = np.rad2deg(rot_to_euler_batch(expmap_batch(pose_arr)))
                for j, field in enumerate(ANGLE_FIELDS):
                    table[field] = eulers[:, j]
        table[R["CLASS"]] = np.asarray(class_values).reshape(-1) if class_values is not None else cls
        if minphic > 0:
            keep &= prob >= minphic
        return keep

    if "alignments2D/class_posterior" in names:
        log.info("Assigning pose and class from 2-D classification")
        posterior = np.asarray(cs["alignments2D/class_posterior"])
        if "alignments2D/split" in names:
            table[R["RANDOMSUBSET"]] = np.asarray(cs["alignments2D/split"]).reshape(-1)
        if "alignments2D/shift" in names:
            assign_vector(table, ORIGIN_FIELDS[:2], np.asarray(cs["alignments2D/shift"]))
        if "alignments2D/pose" in names:
            table[R["ANGLEPSI"]] = np.rad2deg(np.asarray(cs["alignments2D/pose"]).reshape(-1))
        if "alignments2D/class" in names:
            table[R["CLASS"]] = np.asarray(cs["alignments2D/class"]).reshape(-1)
        # Match pyem: 2-D class posterior values are not filtered by --minphic.
        return keep

    log.info("Particle poses not found")
    return keep


def finalize_coordinates(
    table: ColumnTable,
    *,
    swapxy: bool,
    invertx: bool,
    inverty: bool,
    log: logging.Logger,
) -> None:
    if "__coord_x_frac" not in table or "__coord_y_frac" not in table:
        return
    if "__micrograph_shape_x" not in table or "__micrograph_shape_y" not in table:
        log.warning("Normalized coordinates found, but location/micrograph_shape is absent")
        return
    x = np.asarray(table["__coord_x_frac"], dtype=np.float64).copy()
    y = np.asarray(table["__coord_y_frac"], dtype=np.float64).copy()
    if invertx:
        x = 1.0 - x
    if inverty:
        y = 1.0 - y
    shape_x = np.asarray(table["__micrograph_shape_x"])
    shape_y = np.asarray(table["__micrograph_shape_y"])
    if swapxy:
        # pyem default: [x_frac,y_frac] * reversed CryoSPARC [y,x] shape.
        table[R["COORDX"]] = np.rint(x * shape_x).astype(np.int64)
        table[R["COORDY"]] = np.rint(y * shape_y).astype(np.int64)
    else:
        table[R["COORDX"]] = np.rint(x * shape_y).astype(np.int64)
        table[R["COORDY"]] = np.rint(y * shape_x).astype(np.int64)


# ------------------------------ STAR parsing ------------------------------


def parse_star_loops(path: str) -> Dict[str, ColumnTable]:
    """Parse loop_ tables from a STAR file using only the standard library."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        lines = fh.readlines()

    tables: Dict[str, ColumnTable] = {}
    i = 0
    current_data = "data_"
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("data_"):
            current_data = stripped
            i += 1
            continue
        if stripped != "loop_":
            i += 1
            continue
        i += 1
        headers: List[str] = []
        while i < len(lines):
            s = lines[i].strip()
            if s.startswith("_"):
                headers.append(s.split()[0].lstrip("_"))
                i += 1
            else:
                break
        rows: List[List[str]] = []
        while i < len(lines):
            s = lines[i].strip()
            if not s or s.startswith("data_") or s == "loop_" or s.startswith("_"):
                break
            if not s.startswith("#"):
                tokens = shlex.split(lines[i], comments=False, posix=True)
                if len(tokens) >= len(headers):
                    rows.append(tokens[:len(headers)])
            i += 1
        if headers:
            table = ColumnTable(len(rows))
            if rows:
                matrix = np.asarray(rows, dtype=object)
                for j, header in enumerate(headers):
                    col = matrix[:, j]
                    converted: np.ndarray
                    try:
                        converted = col.astype(np.int64)
                    except (ValueError, TypeError):
                        try:
                            converted = col.astype(np.float64)
                        except (ValueError, TypeError):
                            converted = col.astype(object)
                    table[header] = converted
            tables[current_data] = table
        continue
    return tables


def canonical_image_key(values: np.ndarray, strip_uids: bool = False) -> np.ndarray:
    out = []
    for raw in decode_strings(values):
        s = str(raw)
        if "@" in s:
            idx, path = s.split("@", 1)
            if strip_uids:
                path = UID_PREFIX_RE.sub("", path)
            out.append(f"{idx}@{os.path.basename(path)}")
        else:
            if strip_uids:
                s = UID_PREFIX_RE.sub("", s)
            out.append(os.path.basename(s))
    return np.asarray(out, dtype=object)


def copy_coordinates_from_star(table: ColumnTable, pattern: str, log: logging.Logger) -> None:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No STAR files matched {pattern!r}")
    source_parts: List[ColumnTable] = []
    for path in paths:
        parsed = parse_star_loops(path)
        source = parsed.get("data_particles")
        if source is None:
            source = next((t for t in parsed.values() if R["IMAGE_NAME"] in t), None)
        if source is not None:
            source_parts.append(source)
    if not source_parts:
        raise ValueError("No particle loop containing rlnImageName was found in coordinate STAR file(s)")

    fields = [R["MICROGRAPH_NAME"], R["COORDX"], R["COORDY"], R["COORDZ"]]
    source_rows: Dict[str, Tuple[ColumnTable, int]] = {}
    for source in source_parts:
        if R["IMAGE_NAME"] not in source:
            continue
        keys = canonical_image_key(source[R["IMAGE_NAME"]], strip_uids=False)
        for i, key in enumerate(keys):
            source_rows.setdefault(str(key), (source, i))

    target_keys = canonical_image_key(table[R["IMAGE_NAME"]], strip_uids=False)
    matches = [source_rows.get(str(k)) for k in target_keys]
    if sum(m is not None for m in matches) == 0:
        source_rows.clear()
        for source in source_parts:
            if R["IMAGE_NAME"] not in source:
                continue
            keys = canonical_image_key(source[R["IMAGE_NAME"]], strip_uids=True)
            for i, key in enumerate(keys):
                source_rows.setdefault(str(key), (source, i))
        target_keys = canonical_image_key(table[R["IMAGE_NAME"]], strip_uids=True)
        matches = [source_rows.get(str(k)) for k in target_keys]

    matched = sum(m is not None for m in matches)
    log.info("Coordinate STAR merge matched %d / %d particles", matched, table.nrows)
    if matched == 0:
        raise ValueError("Could not match coordinate STAR rows to converted particles")

    for field in fields:
        available = any(field in src for src in source_parts)
        if not available:
            continue
        existing = table.get(field)
        if existing is not None:
            out = existing.copy()
        else:
            numeric = field != R["MICROGRAPH_NAME"]
            out = np.full(table.nrows, np.nan if numeric else "", dtype=np.float64 if numeric else object)
        for i, match in enumerate(matches):
            if match is not None:
                src, j = match
                if field in src:
                    out[i] = src[field][j]
        table[field] = out


# --------------------------- Final conversion steps ---------------------------


def construct_image_names(table: ColumnTable) -> None:
    if IMAGE_PATH not in table or IMAGE_INDEX not in table:
        return
    paths = clean_path_array(table[IMAGE_PATH])
    indices = np.asarray(table[IMAGE_INDEX]).astype(np.int64, copy=False)
    table[R["IMAGE_NAME"]] = np.array(
        [f"{idx + 1:06d}@{path}" for idx, path in zip(indices, paths)], dtype=object
    )


def check_and_convert_defaults(table: ColumnTable, *, relion2: bool, log: logging.Logger) -> None:
    if R["PHASESHIFT"] not in table:
        table[R["PHASESHIFT"]] = np.zeros(table.nrows, dtype=np.float64)

    if R["DEFOCUSANGLE"] in table:
        table[R["DEFOCUSANGLE"]] = np.rad2deg(np.asarray(table[R["DEFOCUSANGLE"]], dtype=np.float64))
    if R["PHASESHIFT"] in table:
        # CryoSPARC stores phase shift in radians.
        table[R["PHASESHIFT"]] = np.rad2deg(np.asarray(table[R["PHASESHIFT"]], dtype=np.float64))

    if R["RANDOMSUBSET"] in table:
        subset = np.asarray(table[R["RANDOMSUBSET"]])
        if np.unique(subset).size == 1:
            table.pop(R["RANDOMSUBSET"])
        else:
            table[R["RANDOMSUBSET"]] = subset.astype(np.int64) + 1

    if R["CLASS"] in table:
        table[R["CLASS"]] = np.asarray(table[R["CLASS"]]).astype(np.int64) + 1

    if R["OPTICSGROUP"] in table:
        table[R["OPTICSGROUP"]] = np.asarray(table[R["OPTICSGROUP"]]).astype(np.int64) + 1
    else:
        table[R["OPTICSGROUP"]] = np.ones(table.nrows, dtype=np.int64)

    psize = table.get(R["IMAGEPIXELSIZE"])
    for pix, ang in zip(ORIGIN_FIELDS, ORIGIN_ANGST_FIELDS):
        if pix in table and ang not in table:
            if psize is None:
                if not relion2:
                    raise ValueError(
                        f"{pix} is present but blob/psize_A is missing; cannot create {ang}"
                    )
            else:
                table[ang] = np.asarray(table[pix], dtype=np.float64) * np.asarray(psize, dtype=np.float64)
        elif ang in table and pix not in table and psize is not None:
            table[pix] = np.asarray(table[ang], dtype=np.float64) / np.asarray(psize, dtype=np.float64)

    dimension = 3 if (R["ORIGINZANGST"] in table or R["COORDZ"] in table) else 2
    table[R["IMAGEDIMENSION"]] = np.full(table.nrows, dimension, dtype=np.int64)
    groups = np.asarray(table[R["OPTICSGROUP"]]).astype(np.int64)
    table[R["OPTICSGROUPNAME"]] = np.array([f"opticsGroup{g}" for g in groups], dtype=object)

    if relion2 and psize is not None:
        if R["DETECTORPIXELSIZE"] not in table:
            table[R["DETECTORPIXELSIZE"]] = np.asarray(psize, dtype=np.float64)
        if R["MAGNIFICATION"] not in table:
            table[R["MAGNIFICATION"]] = np.full(table.nrows, 10000.0)


def apply_boxsize_scale(table: ColumnTable, boxsize: Optional[float]) -> None:
    """Rescale refinement shifts when the refinement box differs from the particle box.

    This is intentionally applied after passthrough merging because blob/shape may
    reside only in the passthrough file.
    """
    if boxsize is None or R["IMAGESIZE"] not in table:
        return
    image_size = np.asarray(table[R["IMAGESIZE"]], dtype=np.float64)
    if image_size.size == 0:
        return
    # pyem uses the particle image box divided by the refinement box.  Normally
    # image size is constant; support row-dependent sizes at no extra cost.
    factor = image_size / float(boxsize)
    for name in ORIGIN_FIELDS:
        if name in table:
            table[name] = np.asarray(table[name], dtype=np.float64) * factor


def apply_class_filter(table: ColumnTable, classes: Optional[Sequence[int]]) -> ColumnTable:
    if not classes:
        return table
    if R["CLASS"] not in table:
        raise ValueError("--class was requested, but no class assignments are present")
    wanted = np.asarray(sorted(set(classes)), dtype=np.int64)
    keep = np.isin(np.asarray(table[R["CLASS"]]).astype(np.int64), wanted)
    return table.subset(keep)


def prepare_relion_version(table: ColumnTable, *, relion2: bool) -> None:
    if relion2:
        for name in ORIGIN_ANGST_FIELDS + [
            R["BEAMTILTX"], R["BEAMTILTY"], R["OPTICSGROUP"], R["OPTICSGROUPNAME"],
            R["MAGMAT00"], R["MAGMAT01"], R["MAGMAT10"], R["MAGMAT11"],
            R["IMAGEPIXELSIZE"], R["IMAGESIZE"], R["IMAGEDIMENSION"],
        ]:
            table.pop(name)
    else:
        for name in ORIGIN_FIELDS + [R["MAGNIFICATION"], R["DETECTORPIXELSIZE"]]:
            table.pop(name)


def sort_table_columns(table: ColumnTable, columns: Optional[Sequence[str]] = None) -> List[str]:
    available = table.public_columns() if columns is None else [c for c in columns if c in table]
    ordered = [c for c in FIELD_ORDER if c in available]
    ordered.extend(c for c in available if c not in ordered)
    return ordered


# ------------------------------- STAR writer -------------------------------


def format_star_value(value: object) -> str:
    if isinstance(value, (np.integer, int)) and not isinstance(value, bool):
        return str(int(value))
    if isinstance(value, (np.floating, float)):
        x = float(value)
        if math.isnan(x):
            return "nan"
        if math.isinf(x):
            return "inf" if x > 0 else "-inf"
        return f"{x:.6f}"
    if isinstance(value, (bytes, np.bytes_)):
        s = bytes(value).decode("utf-8", errors="replace")
    else:
        s = str(value)
    if s == "":
        return "''"
    if any(ch.isspace() for ch in s) or s.startswith("#") or s.startswith(";"):
        if "'" not in s:
            return f"'{s}'"
        return '"' + s.replace('"', '\\"') + '"'
    return s


def write_loop(
    fh,
    table_name: str,
    table: ColumnTable,
    columns: Sequence[str],
    row_indices: Optional[np.ndarray] = None,
    chunk_size: int = 4096,
) -> None:
    fh.write(f"\n{table_name}\n\nloop_\n")
    for i, name in enumerate(columns, start=1):
        fh.write(f"_{name} #{i}\n")
    arrays = [table[name] for name in columns]
    indices = np.arange(table.nrows) if row_indices is None else np.asarray(row_indices)
    buffer: List[str] = []
    for idx in indices:
        buffer.append(" ".join(format_star_value(arr[idx]) for arr in arrays) + "\n")
        if len(buffer) >= chunk_size:
            fh.writelines(buffer)
            buffer.clear()
    if buffer:
        fh.writelines(buffer)


def write_star(path: str, table: ColumnTable, *, relion2: bool) -> None:
    if not path.endswith(".star"):
        path += ".star"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(f"# relion 30001\n")
        if relion2:
            cols = sort_table_columns(table)
            write_loop(fh, "data_", table, cols)
            return

        groups = np.asarray(table[R["OPTICSGROUP"]]).astype(np.int64)
        unique_groups = np.unique(groups)
        first_indices = np.array([np.flatnonzero(groups == g)[0] for g in unique_groups], dtype=np.int64)
        optics_cols = [name for name in OPTICS_FIELDS if name in table]
        # Keep group name then group number at the front, as RELION normally writes them.
        optics_cols = [c for c in [R["OPTICSGROUPNAME"], R["OPTICSGROUP"]] if c in optics_cols] + [
            c for c in optics_cols if c not in (R["OPTICSGROUPNAME"], R["OPTICSGROUP"])
        ]
        write_loop(fh, "data_optics", table, optics_cols, row_indices=first_indices)

        particle_cols = [c for c in table.public_columns() if c not in OPTICS_FIELDS or c == R["OPTICSGROUP"]]
        particle_cols = sort_table_columns(table, particle_cols)
        write_loop(fh, "data_particles", table, particle_cols)


# ---------------------------------- Main ----------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert CryoSPARC v2+ .cs particle metadata to RELION STAR using only NumPy.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", nargs="+", help="Primary .cs followed by optional passthrough .cs files")
    parser.add_argument("output", help="Output .star file")
    parser.add_argument("--boxsize", type=float, help="CryoSPARC refinement box size if different from particle images")
    parser.add_argument("--class", dest="classes", action="append", type=int, help="Keep this 1-based class; repeatable")
    parser.add_argument("--minphic", type=float, default=0.0, help="Minimum selected class posterior probability")
    parser.add_argument("--stack-path", type=str, help="Replace all particle stack paths with this path")
    parser.add_argument("--micrograph-path", type=str, help="Replace micrograph directories, preserving basenames")
    parser.add_argument("--copy-micrograph-coordinates", type=str, help="STAR file or quoted glob supplying micrograph names/coordinates")
    parser.add_argument("--cached", action="store_true", help="Accepted for CLI compatibility; no effect")
    parser.add_argument("--swapxy", action="store_true", help="Axis swapping is already the default; retained for compatibility")
    parser.add_argument("--noswapxy", action="store_true", help="Do not swap X/Y when converting normalized coordinates")
    parser.add_argument("--invertx", action="store_true", help="Invert normalized coordinate X before conversion")
    parser.add_argument("--no-inverty", action="store_true", help="Disable the default normalized-coordinate Y inversion")
    parser.add_argument(
        "--inverty", dest="no_inverty", action="store_true",
        help="Compatibility alias: pyem uses this option to disable its default Y inversion",
    )
    parser.add_argument("--flipy", action="store_true", help="Flip refined Y shifts, poses, and defocus angles")
    parser.add_argument("--flipy-pose", action="store_true", help="Flip refined Y shifts and particle poses")
    parser.add_argument("--flipy-ctf", action="store_true", help="Flip defocus angles")
    parser.add_argument("--transform", type=str, help="JSON 3x3 rotation or 3x4 rotation+translation matrix")
    parser.add_argument("--relion2", "-r2", action="store_true", help="Write a RELION 2-style single data_ table")
    parser.add_argument("--strip-uid", nargs="?", const=-1, type=int, default=None,
                        help="Strip all (or N) leading 21-digit CryoSPARC UID prefixes from paths")
    parser.add_argument("--10k", dest="first10k", action="store_true", help="Convert only the first 10,000 rows")
    parser.add_argument("--allow-pickle", action="store_true", help="Allow pickle in np.load; unsafe for untrusted files")
    parser.add_argument("--max-header-size", type=int, default=100000, help="NumPy maximum .npy header size")
    parser.add_argument("--movies", action="store_true", help="Not implemented in this NumPy-only particle converter")
    parser.add_argument("--loglevel", "-l", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return parser


def run(args: argparse.Namespace) -> int:
    logging.basicConfig(level=getattr(logging, args.loglevel), format="%(levelname)s: %(message)s")
    log = logging.getLogger("csparc2star_numpy")

    if args.movies:
        raise NotImplementedError("--movies trajectory export is not implemented; particle .cs conversion is supported")
    if not args.input:
        raise ValueError("At least one input .cs file is required")
    if not args.input[0].endswith(".cs"):
        raise ValueError("Only CryoSPARC v2+ .cs input is supported")

    primary_cs = load_cs(args.input[0], args.max_header_size, args.allow_pickle)
    if args.first10k:
        primary_cs = primary_cs[:10000]
    log.info("Read %d rows from primary file %s", primary_cs.shape[0], args.input[0])

    table, keep = extract_common(
        primary_cs, include_model=True, minphic=args.minphic, log=log
    )
    for path in args.input[1:]:
        if not path.endswith(".cs"):
            log.warning("Ignoring non-.cs auxiliary input %s", path)
            continue
        aux_cs = load_cs(path, args.max_header_size, args.allow_pickle)
        if args.first10k:
            aux_cs = aux_cs[:10000]
        aux, _ = extract_common(aux_cs, include_model=False, minphic=0.0, log=log)
        log.info("Merging auxiliary file %s", path)
        merge_tables_by_uid(table, aux, log)

    apply_boxsize_scale(table, args.boxsize)

    if not keep.all():
        log.info("Posterior filter retained %d / %d rows", int(keep.sum()), keep.size)
        table = table.subset(keep)

    finalize_coordinates(
        table,
        swapxy=not args.noswapxy,
        invertx=args.invertx,
        inverty=not args.no_inverty,
        log=log,
    )

    # Path normalization/replacement before constructing rlnImageName.
    if IMAGE_PATH in table:
        table[IMAGE_PATH] = clean_path_array(table[IMAGE_PATH])
        if args.stack_path:
            table[IMAGE_PATH] = np.full(table.nrows, args.stack_path, dtype=object)
        if args.strip_uid is not None:
            table[IMAGE_PATH] = strip_uid_prefixes(table[IMAGE_PATH], count=args.strip_uid)
    if R["MICROGRAPH_NAME"] in table:
        table[R["MICROGRAPH_NAME"]] = clean_path_array(table[R["MICROGRAPH_NAME"]])
        if args.strip_uid is not None:
            table[R["MICROGRAPH_NAME"]] = strip_uid_prefixes(table[R["MICROGRAPH_NAME"]], count=args.strip_uid)
        if args.micrograph_path:
            table[R["MICROGRAPH_NAME"]] = replace_directory(table[R["MICROGRAPH_NAME"]], args.micrograph_path)

    construct_image_names(table)

    if args.copy_micrograph_coordinates:
        if R["IMAGE_NAME"] not in table:
            raise ValueError("Cannot merge coordinates because rlnImageName could not be constructed")
        copy_coordinates_from_star(table, args.copy_micrograph_coordinates, log)

    # Pose/CTF flips occur while origins are still in pixels, matching pyem order.
    if args.flipy or args.flipy_pose:
        if R["ORIGINY"] in table:
            table[R["ORIGINY"]] = -np.asarray(table[R["ORIGINY"]], dtype=np.float64)
        if table_has_3d_angles(table):
            apply_transform(table, np.diag([1.0, -1.0, -1.0]), leftmult=True, log=log)
        elif R["ANGLEPSI"] in table:
            table[R["ANGLEPSI"]] = -np.asarray(table[R["ANGLEPSI"]], dtype=np.float64)

    if args.flipy or args.flipy_ctf:
        if R["DEFOCUSANGLE"] in table:
            # At this point defocus angle is still radians.
            table[R["DEFOCUSANGLE"]] = -np.asarray(table[R["DEFOCUSANGLE"]], dtype=np.float64)

    if args.transform:
        matrix = np.asarray(json.loads(args.transform), dtype=np.float64)
        apply_transform(table, matrix, leftmult=False, log=log)

    check_and_convert_defaults(table, relion2=args.relion2, log=log)
    table = apply_class_filter(table, args.classes)
    prepare_relion_version(table, relion2=args.relion2)

    if table.nrows == 0:
        raise ValueError("No particles remain after filtering")
    if R["IMAGE_NAME"] not in table:
        log.warning("rlnImageName is absent because blob/path or blob/idx was unavailable")

    write_star(args.output, table, relion2=args.relion2)
    log.info("Wrote %d particles to %s", table.nrows, args.output)
    log.info("Output fields: %s", ", ".join(table.public_columns()))
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except Exception as exc:
        logging.basicConfig(level=logging.ERROR, format="%(levelname)s: %(message)s")
        logging.getLogger("csparc2star_numpy").error("%s", exc)
        if getattr(args, "loglevel", "INFO") == "DEBUG":
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
