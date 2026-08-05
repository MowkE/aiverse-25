"""Metric correctness: known values, bounds, and edge-case conventions."""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from universe25.metrics import entropy, gini, normalized_hhi


class TestGini:
    def test_equal_distribution_is_zero(self):
        assert gini(np.array([3.0, 3.0, 3.0, 3.0])) == pytest.approx(0.0)

    def test_single_holder(self):
        # For one holder among n, Gini = (n-1)/n.
        assert gini(np.array([0.0, 0.0, 0.0, 5.0])) == pytest.approx(3 / 4)

    def test_all_zero_convention(self):
        assert gini(np.zeros(8)) == 0.0

    def test_known_value(self):
        assert gini(np.array([1.0, 3.0])) == pytest.approx(0.25)

    def test_rejects_negative(self):
        with pytest.raises(ValueError):
            gini(np.array([-1.0, 2.0]))


class TestNormalizedHHI:
    def test_equal_distribution_is_zero(self):
        assert normalized_hhi(np.ones(8)) == pytest.approx(0.0)

    def test_single_holder_is_one(self):
        assert normalized_hhi(np.array([0.0, 0.0, 7.0])) == pytest.approx(1.0)

    def test_all_zero_convention(self):
        assert normalized_hhi(np.zeros(8)) == 0.0


class TestEntropy:
    def test_uniform_is_log_n(self):
        assert entropy(np.array([2.0, 2.0, 2.0])) == pytest.approx(np.log(3))

    def test_degenerate_is_zero(self):
        assert entropy(np.array([5.0, 0.0, 0.0])) == pytest.approx(0.0)

    def test_empty_convention(self):
        assert entropy(np.zeros(3)) == 0.0


@given(st.lists(st.floats(min_value=0.0, max_value=1e6), min_size=2, max_size=32))
def test_gini_bounds(values):
    g = gini(np.array(values))
    assert 0.0 <= g < 1.0


@given(st.lists(st.floats(min_value=0.0, max_value=1e6), min_size=2, max_size=32))
def test_nhhi_bounds(values):
    h = normalized_hhi(np.array(values))
    assert 0.0 <= h <= 1.0 + 1e-12


@given(st.lists(st.floats(min_value=0.0, max_value=1e6), min_size=1, max_size=16))
def test_entropy_bounds(counts):
    h = entropy(np.array(counts))
    assert 0.0 <= h <= np.log(len(counts)) + 1e-9
