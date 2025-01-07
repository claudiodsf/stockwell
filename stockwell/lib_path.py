# SPDX-License-Identifier: GPL-3.0-or-later
"""
lib_path.py

Function to get the path to the compiled libraries.

This file is part of the Stockwell project.

:copyright:
    2023-2025 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
import os
import importlib.machinery


def get_lib_path(lib):
    """
    Return the path to the compiled library.

    Parameters
    ----------
    lib : str
        The name of the library.

    Returns
    -------
    str
        The path to the compiled library.
    """
    suffix = importlib.machinery.EXTENSION_SUFFIXES[0]
    libname = lib + suffix
    return os.path.join(os.path.dirname(__file__), 'lib', libname)
