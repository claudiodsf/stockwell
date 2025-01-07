# SPDX-License-Identifier: GPL-3.0-or-later
"""
test_stockwell.py

This file is part of the Stockwell project.

:copyright:
    2023-2025 Claudio Satriano <satriano@ipgp.fr>

:license:
    GNU General Public License v3.0 or later.
    (https://www.gnu.org/licenses/gpl-3.0.html)
"""
import os
import unittest
import numpy as np
from numpy.testing import assert_allclose
from stockwell.lib_path import get_lib_path

# Note: st and sine modules are lazily imported in the tests below to avoid
# early failure if the libraries are not found.
# pylint: disable=import-outside-toplevel


class TestStockwell(unittest.TestCase):
    """Test the Stockwell transform."""
    def test_find_libs(self):
        """Test if the compiled libraries are found."""
        for lib in 'st', 'sine':
            lib_path = get_lib_path(lib)
            # check if the library exists
            if not os.path.exists(lib_path):
                print(f'Library not found: {lib_path}')
                assert False

    def test_st(self):
        """Test the Stockwell transform."""
        from stockwell import st
        array = np.array([0, 1])
        stock_expected = np.array([
            [0.5+0.j,  0.5+0.j],
            [-0.5+0.j, -0.5+0.j]
        ])
        stock = st.st(array)
        assert_allclose(stock, stock_expected)

    def test_ist(self):
        """Test the inverse Stockwell transform."""
        from stockwell import st
        stock = np.array([
            [0.5+0.j,  0.5+0.j],
            [-0.5+0.j, -0.5+0.j]
        ])
        array_expected = np.array([0, 1])
        array = st.ist(stock)
        assert_allclose(array, array_expected)

    def test_hilbert(self):
        """Test the Hilbert transform."""
        from stockwell import st
        array = np.arange(10)
        hilbert_expected = np.array([
            0.+5.50552768j, 1.-0.64983939j, 2.-0.64983939j, 3.-2.10292445j,
            4.-2.10292445j, 5.-2.10292445j, 6.-2.10292445j, 7.-0.64983939j,
            8.-0.64983939j, 9.+5.50552768j])
        hilbert = st.hilbert(array)
        assert_allclose(hilbert, hilbert_expected)

    def test_sine_taper(self):
        """Test the sine taper."""
        from stockwell import sine
        taper_expected = np.array([
            0.12013117, 0.23053002, 0.3222527, 0.38786839, 0.42206128,
            0.42206128, 0.38786839, 0.3222527, 0.23053002, 0.12013117])
        taper = sine.sine_taper(0, 10)
        assert_allclose(taper, taper_expected)


if __name__ == '__main__':
    unittest.main()
