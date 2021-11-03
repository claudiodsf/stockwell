# -*- coding: utf8 -*-
from unittest import TestCase
from stockwell import st
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
