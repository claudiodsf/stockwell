# SPDX-License-Identifier: GPL-3.0-or-later
"""
test_stockwell.py.

This file is part of the Stockwell project.

:copyright:
    2023-2026 Claudio Satriano <satriano@ipgp.fr>

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


class TestFindLibs(unittest.TestCase):
    """Test that the compiled libraries are found."""

    def test_find_libs(self):
        """Test if the compiled libraries are found."""
        for lib in 'st', 'sine':
            with self.subTest(lib=lib):
                lib_path = get_lib_path(lib)
                self.assertTrue(
                    os.path.exists(lib_path),
                    f'Library not found: {lib_path}'
                )


class TestStockwellTransform(unittest.TestCase):
    """Test the Stockwell forward transform (st)."""

    def setUp(self):
        """Import the st module lazily."""
        from stockwell import st  # pylint: disable=import-outside-toplevel
        self.st = st

    def test_st_basic(self):
        """Test st with the minimal [0, 1] array."""
        array = np.array([0, 1])
        stock_expected = np.array([
            [0.5 + 0.j, 0.5 + 0.j],
            [-0.5 + 0.j, -0.5 + 0.j]
        ])
        stock = self.st.st(array)
        assert_allclose(stock, stock_expected)

    def test_st_input_validation(self):
        """Test st raises on invalid inputs."""
        # 2D input
        with self.assertRaises(ValueError):
            self.st.st(np.ones((4, 4)))
        # non-integer lo
        with self.assertRaises(ValueError):
            self.st.st(np.arange(8), lo=1.5)
        # non-integer hi
        with self.assertRaises(ValueError):
            self.st.st(np.arange(8), hi=3.7)
        # invalid win_type
        with self.assertRaises(ValueError):
            self.st.st(np.arange(8), win_type='invalid')
        # empty array
        with self.assertRaises(ValueError):
            self.st.st(np.array([], dtype=float))

    def test_st_kazemi_window(self):
        """Test st with the Kazemi window type."""
        data = np.arange(16, dtype=float)
        result = self.st.st(data, win_type='kazemi')
        self.assertEqual(result.shape, (9, 16))
        self.assertTrue(np.all(np.isfinite(result)))

    def test_st_roundtrip(self):
        """Test that ist(st(x)) recovers the original signal."""
        n = 128
        data = np.random.randn(n)
        stock = self.st.st(data)
        recovered = self.st.ist(stock)
        assert_allclose(recovered, data, atol=1e-12)

    def test_st_readme_chirp(self):
        """Test the chirp example from the README."""
        # Linear chirp from 12.5 Hz down to 2.5 Hz over 10 s
        t = np.linspace(0, 10, 5001)
        f0 = 12.5
        f1 = 2.5
        w = np.sin(2 * np.pi * (f0 * t + (f1 - f0) * t**2 / (2 * t[-1])))

        fmin = 0   # Hz
        fmax = 25  # Hz
        df = 1.0 / (t[-1] - t[0])
        fmin_samples = int(fmin / df)
        fmax_samples = int(fmax / df)

        stock = self.st.st(w, fmin_samples, fmax_samples)
        expected_freqs = fmax_samples - fmin_samples + 1
        self.assertEqual(stock.shape, (expected_freqs, len(t)))
        self.assertTrue(np.all(np.isfinite(stock)))

        # Roundtrip with a frequency subset is approximate —
        # only frequencies between fmin and fmax are preserved.
        recovered = self.st.ist(stock, fmin_samples, fmax_samples)
        # Check correlation between original and reconstructed signal
        corr = np.corrcoef(recovered, w)[0, 1]
        self.assertGreater(corr, 0.99)


class TestInverseStockwell(unittest.TestCase):
    """Test the inverse Stockwell transform (ist)."""

    def setUp(self):
        """Import the st module lazily."""
        from stockwell import st  # pylint: disable=import-outside-toplevel
        self.st = st

    def test_ist_basic(self):
        """Test ist with the minimal 2x2 matrix."""
        stock = np.array([
            [0.5 + 0.j, 0.5 + 0.j],
            [-0.5 + 0.j, -0.5 + 0.j]
        ])
        array_expected = np.array([0, 1])
        array = self.st.ist(stock)
        assert_allclose(array, array_expected)

    def test_ist_input_validation(self):
        """Test ist raises on invalid inputs."""
        # 1D input
        with self.assertRaises(ValueError):
            self.st.ist(np.arange(8))
        # non-integer lo
        with self.assertRaises(ValueError):
            self.st.ist(np.ones((4, 8)), lo=0.5)
        # non-integer hi
        with self.assertRaises(ValueError):
            self.st.ist(np.ones((4, 8)), hi=3.5)
        # dimension mismatch
        with self.assertRaises(ValueError):
            self.st.ist(np.ones((4, 8)), lo=0, hi=10)
        # empty array
        with self.assertRaises(ValueError):
            self.st.ist(np.ones((4, 0), dtype=complex))


class TestHilbert(unittest.TestCase):
    """Test the Hilbert transform."""

    def setUp(self):
        """Import the st module lazily."""
        from stockwell import st  # pylint: disable=import-outside-toplevel
        self.st = st

    def test_hilbert_basic(self):
        """Test hilbert with a known array."""
        array = np.arange(10)
        hilbert_expected = np.array([
            0. + 5.50552768j, 1. - 0.64983939j, 2. - 0.64983939j,
            3. - 2.10292445j, 4. - 2.10292445j, 5. - 2.10292445j,
            6. - 2.10292445j, 7. - 0.64983939j, 8. - 0.64983939j,
            9. + 5.50552768j
        ])
        hilbert = self.st.hilbert(array)
        assert_allclose(hilbert, hilbert_expected)

    def test_hilbert_input_validation(self):
        """Test hilbert raises on invalid inputs."""
        with self.assertRaises(ValueError):
            self.st.hilbert(np.ones((4, 4)))
        with self.assertRaises(ValueError):
            self.st.hilbert(np.array([], dtype=float))


class TestSineTaper(unittest.TestCase):
    """Test the sine taper."""

    def setUp(self):
        """Import the sine module lazily."""
        from stockwell import sine  # pylint: disable=import-outside-toplevel
        self.sine = sine

    def test_sine_taper_basic(self):
        """Test sine_taper with known values."""
        taper_expected = np.array([
            0.12013117, 0.23053002, 0.3222527, 0.38786839, 0.42206128,
            0.42206128, 0.38786839, 0.3222527, 0.23053002, 0.12013117
        ])
        taper = self.sine.sine_taper(0, 10)
        assert_allclose(taper, taper_expected)

    def test_sine_taper_input_validation(self):
        """Test sine_taper raises on invalid inputs."""
        with self.assertRaises(ValueError):
            self.sine.sine_taper(1.5, 10)
        with self.assertRaises(ValueError):
            self.sine.sine_taper(0, 10.5)
        with self.assertRaises(ValueError):
            self.sine.sine_taper(0, 0)
        with self.assertRaises(ValueError):
            self.sine.sine_taper(0, -1)

    def test_sine_taper_orthogonality(self):
        """Test that sine tapers are orthogonal."""
        n = 10
        tapers = [self.sine.sine_taper(k, n) for k in range(5)]
        for i in range(5):
            for j in range(5):
                with self.subTest(i=i, j=j):
                    dot = np.dot(tapers[i], tapers[j])
                    expected = 1.0 if i == j else 0.0
                    self.assertAlmostEqual(
                        dot, expected, places=10,
                        msg=f'dot mismatch for i={i}, j={j}'
                    )


if __name__ == '__main__':
    unittest.main()
