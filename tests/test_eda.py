"""Unit tests for src.eda.

Run with: pytest tests/
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.eda import adf_test, rolling_volatility


def test_adf_test_too_few_observations():
    with pytest.raises(ValueError):
        adf_test(pd.Series([1.0, 2.0, 3.0]), name="tiny series")


def test_adf_test_returns_expected_keys():
    rng = np.random.default_rng(42)
    stationary = pd.Series(rng.normal(0, 1, size=200))
    result = adf_test(stationary, name="synthetic noise")
    assert set(result.keys()) == {
        "name",
        "adf_statistic",
        "p_value",
        "n_obs",
        "is_stationary_at_5pct",
    }
    # White noise should be strongly stationary.
    assert result["is_stationary_at_5pct"] is True


def test_adf_test_detects_nonstationary_trend():
    trend = pd.Series(np.arange(200, dtype=float))
    result = adf_test(trend, name="linear trend")
    assert result["is_stationary_at_5pct"] is False


def test_rolling_volatility_invalid_window():
    with pytest.raises(ValueError):
        rolling_volatility(pd.Series([0.01, -0.02, 0.03]), window=1)


def test_rolling_volatility_output_length_matches_input():
    series = pd.Series([0.01, -0.02, 0.03, 0.0, -0.01, 0.02] * 10)
    vol = rolling_volatility(series, window=5)
    assert len(vol) == len(series)
    assert vol.name == "RollingVol_5d"
