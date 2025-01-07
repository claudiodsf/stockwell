# SPDX-License-Identifier: GPL-3.0-or-later
"""
sine.py

This file is part of the Stockwell project.

:copyright:
    2023-2025 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
from ctypes import CDLL, POINTER, c_int, c_double, c_void_p
import numpy as np
from .lib_path import get_lib_path

lib_sine = CDLL(get_lib_path('sine'))
lib_sine.sine_taper.argtypes = [
    c_int,  # K
    c_int,  # N
    POINTER(c_double)  # d
]
lib_sine.sine_taper.restype = c_void_p


def sine_taper(K, N):
    """
    Returns the Kth sine taper of length N.

    Parameters
    ----------
    K : int
        Taper index.
    N : int
        Taper length.

    Returns
    -------
    result : ndarray
        The Kth sine taper of length N.

    Notes
    -----
    Riedel & Sidorenko sine tapers.
    """
    if not isinstance(K, int) or not isinstance(N, int):
        raise ValueError('K and N must be integers')
    result = np.zeros(N, dtype=np.double)
    lib_sine.sine_taper(K, N, result.ctypes.data_as(POINTER(c_double)))
    return result
