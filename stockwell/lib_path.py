# SPDX-License-Identifier: GPL-3.0-or-later
"""
lib_path.py

Function to get the path to the compiled libraries.

This file is part of the Stockwell project.

:copyright:
    2023 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
import os
import sysconfig


def get_lib_path(lib):
    suffix = (
        sysconfig.get_config_var('EXT_SUFFIX') or
        sysconfig.get_config_var('SO')
    )
    if os.name == 'nt':
        py_version_nodot = sysconfig.get_config_var('py_version_nodot')
        platform = sysconfig.get_platform().replace('-', '_')
        suffix = f'.cp{py_version_nodot}-{platform}{suffix}'
    libname = lib + suffix
    return os.path.join(os.path.dirname(__file__), 'lib', libname)
