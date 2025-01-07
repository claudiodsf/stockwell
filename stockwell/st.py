# SPDX-License-Identifier: GPL-3.0-or-later
"""
st.py

This file is part of the Stockwell project.

:copyright:
    2023-2025 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
from ctypes import CDLL, POINTER, c_int, c_uint, c_double, c_void_p
import numpy as np
from .lib_path import get_lib_path

lib_st = CDLL(get_lib_path('st'))
lib_st.st.argtypes = [
    c_int,  # len
    c_int,  # lo
    c_int,  # hi
    c_double,  # gamma
    c_uint,  # window code
    POINTER(c_double),  # data
    POINTER(c_double)  # result
]
lib_st.st.restype = c_void_p
lib_st.ist.argtypes = [
    c_int,  # len
    c_int,  # lo
    c_int,  # hi
    POINTER(c_double),  # data
    POINTER(c_double)  # result
]
lib_st.ist.restype = c_void_p
lib_st.hilbert.argtypes = [
    c_int,  # len
    POINTER(c_double),  # data
    POINTER(c_double)  # result
]
lib_st.hilbert.restype = c_void_p


def st(data, lo=0, hi=None, gamma=1, win_type='gauss'):
    """
    Returns the 2d, complex Stockwell transform of the real array ``data``.

    Parameters
    ----------
    data : array_like
        Input data array.
    lo : int, optional
        Lowest frequency index to return (default 0).
    hi : int, optional
        Highest frequency index to return (default n/2), where n is the
        length of ``data``.
    gamma : float, optional
        Gamma parameter (default 1). See Notes.
    win_type : {'gauss', 'kazemi'}, optional
        Window type (default 'gauss'). See Notes.

    Returns
    -------
    result : ndarray
        The Stockwell transform of ``data``. The first dimension is the
        frequency axis, the second dimension is the time axis.

    Notes
    -----
    If ``lo`` and ``hi`` are specified, only those frequencies (rows)
    are returned;
    If ``hi`` is not specified, then it will be set to n/2, where n is
    the length of ``data``.

    The parameter ``gamma`` (default 1) can be used to tune the time and
    frequency resolutions of the S-transform. It represents the number of
    Fourier sinusoidal periods within one standard deviation of the
    Gaussian window.
    Raising gamma increases the frequency resolution and consequently
    decreases the time resolution of the S-transform and vice versa
    (Kazemi, 2014).

    Two ``win_type`` are available:
    ``'gauss'`` (default) and ``'kazemi'`` (Kazemi, 2014).
    """
    data = np.atleast_1d(np.ascontiguousarray(data, dtype=np.double))
    if data.ndim != 1:
        raise ValueError('x must be a scalar or a 1d array')
    ntimes = len(data)
    if hi is None:
        hi = ntimes // 2
    if not isinstance(hi, int) or not isinstance(lo, int):
        raise ValueError('hi and lo must be integers')
    nfreqs = int(hi - lo + 1)
    if win_type == 'gauss':
        win_code = 0
    elif win_type == 'kazemi':
        win_code = 1
    else:
        raise ValueError(f'Unknown window type: {win_type}')
    result = np.zeros((nfreqs, ntimes), dtype=np.complex128)
    lib_st.st(
        ntimes, lo, hi, gamma, win_code,
        data.ctypes.data_as(POINTER(c_double)),
        result.ctypes.data_as(POINTER(c_double)))
    return result


def ist(data, lo=0, hi=None):
    """
    Returns the inverse Stockwell transform of the 2d, complex array ``data``.

    Parameters
    ----------
    data : array_like
        Input data array, 2d and complex.
    lo : int, optional
        Lowest frequency index to use (default 0).
    hi : int, optional
        Highest frequency index to use (default n/2), where n is the number of
        time samples in ``data``.

    Returns
    -------
    result : ndarray
        The inverse Stockwell transform of ``data``.

    Notes
    -----
    If ``lo`` and ``hi`` are specified, only those frequencies (rows)
    are used;
    If ``hi`` is not specified, then it will be set to n/2, where n is
    the number of time samples in ``data``.
    The difference between ``hi`` and ``lo`` must be equal to the number of
    frequencies in ``data`` minus 1.
    """
    data = np.ascontiguousarray(data, dtype=np.complex128)
    if data.ndim != 2:
        raise ValueError('data must be a 2d array')
    nfreqs, ntimes = data.shape
    if hi is None:
        hi = ntimes // 2
    if not isinstance(hi, int) or not isinstance(lo, int):
        raise ValueError('hi and lo must be integers')
    if nfreqs != hi - lo + 1:
        raise ValueError(
            'the difference between hi and lo must be equal to the number of '
            'frequencies in data (first dimension) minus 1'
        )
    result = np.zeros(ntimes, dtype=np.double)
    lib_st.ist(
        ntimes, lo, hi,
        data.ctypes.data_as(POINTER(c_double)),
        result.ctypes.data_as(POINTER(c_double)))
    return result


def hilbert(data):
    """
    Returns the complex Hilbert transform of the real array ``data``.

    Parameters
    ----------
    data : array_like
        Input data array.

    Returns
    -------
    result : ndarray
        The Hilbert transform of ``data``.
    """
    data = np.atleast_1d(np.ascontiguousarray(data, dtype=np.double))
    if data.ndim != 1:
        raise ValueError('data must be a scalar or a 1d array')
    ntimes = len(data)
    result = np.zeros(ntimes, dtype=np.complex128)
    lib_st.hilbert(
        ntimes,
        data.ctypes.data_as(POINTER(c_double)),
        result.ctypes.data_as(POINTER(c_double)))
    return result
