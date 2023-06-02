# -*- coding: utf8 -*-
from unittest import TestCase
from stockwell import st, sine
import numpy as np
from numpy.testing import assert_allclose


class TestStockwell(TestCase):
    def test_st(self):
        array = np.array([0, 1])
        stock_expected = np.array([
            [0.5+0.j,  0.5+0.j],
            [-0.5+0.j, -0.5+0.j]
        ])
        stock = st.st(array)
        assert_allclose(stock, stock_expected)

    def test_ist(self):
        stock = np.array([
            [0.5+0.j,  0.5+0.j],
            [-0.5+0.j, -0.5+0.j]
        ])
        array_expected = np.array([0, 1])
        array = st.ist(stock)
        assert_allclose(array, array_expected)

    def test_hilbert(self):
        array = np.arange(10)
        hilbert_expected = np.array([
            0.+5.50552768j, 1.-0.64983939j, 2.-0.64983939j, 3.-2.10292445j,
            4.-2.10292445j, 5.-2.10292445j, 6.-2.10292445j, 7.-0.64983939j,
            8.-0.64983939j, 9.+5.50552768j])
        hilbert = st.hilbert(array)
        assert_allclose(hilbert, hilbert_expected)

    def test_sine_taper(self):
        taper_expected = np.array([
            0.12013117, 0.23053002, 0.3222527, 0.38786839, 0.42206128,
            0.42206128, 0.38786839, 0.3222527, 0.23053002, 0.12013117])
        taper = sine.sine_taper(0, 10)
        assert_allclose(taper, taper_expected)
