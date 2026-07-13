"""Tests for src/change_point_model.py.

The MCMC fitting path (fit_change_point_model) is exercised with a tiny
synthetic series and very few draws so the suite stays fast; correctness
of PyMC's sampler itself is out of scope. We focus on: model construction
validation/error paths, that fitting recovers a roughly correct switch
point on an obvious synthetic regime shift, and the nearest_events helper.
"""

import numpy as np
import pandas as pd
import pytest

from src.change_point_model import (
    ChangePointModelError,
    build_change_point_model,
    fit_change_point_model,
    nearest_events,
)


def test_build_change_point_model_rejects_too_short_series():
    with pytest.raises(ChangePointModelError):
        build_change_point_model(np.array([0.1, 0.2, 0.3]))


def test_build_change_point_model_rejects_nans():
    values = np.concatenate([np.zeros(20), [np.nan], np.zeros(20)])
    with pytest.raises(ChangePointModelError):
        build_change_point_model(values)


def test_build_change_point_model_rejects_non_1d():
    with pytest.raises(ChangePointModelError):
        build_change_point_model(np.zeros((10, 2)))


def test_build_change_point_model_returns_expected_variables():
    values = np.random.default_rng(0).normal(size=50)
    model = build_change_point_model(values)
    var_names = {rv.name for rv in model.free_RVs}
    assert {"tau", "mu1", "mu2", "sigma1", "sigma2"}.issubset(var_names)


def test_fit_change_point_model_mismatched_lengths_raises():
    dates = pd.date_range("2020-01-01", periods=10)
    values = np.zeros(5)
    with pytest.raises(ChangePointModelError):
        fit_change_point_model(dates, values, draws=10, tune=10, chains=1, cores=1)


def test_fit_change_point_model_recovers_obvious_switch_point():
    rng = np.random.default_rng(42)
    n_before, n_after = 60, 60
    before = rng.normal(loc=0.0, scale=0.01, size=n_before)
    after = rng.normal(loc=2.0, scale=0.01, size=n_after)
    values = np.concatenate([before, after])
    dates = pd.Series(pd.date_range("2020-01-01", periods=len(values), freq="D"))

    fit = fit_change_point_model(
        dates, values, draws=200, tune=200, chains=2, cores=1, random_seed=1
    )

    tau_samples = fit.trace.posterior["tau"].values.flatten()
    tau_mean = tau_samples.mean()
    # The true switch is at index n_before - 1; allow a generous tolerance
    # since this is a short/low-draw fit purely to check plumbing works.
    assert abs(tau_mean - (n_before - 1)) < 15


def test_nearest_events_requires_date_column():
    with pytest.raises(ChangePointModelError):
        nearest_events(pd.Timestamp("2020-01-01"), pd.DataFrame({"event_name": ["x"]}))


def test_nearest_events_orders_by_distance_and_flags_window():
    events = pd.DataFrame(
        {
            "event_id": [1, 2, 3],
            "date": pd.to_datetime(["2020-01-01", "2020-06-01", "2020-01-10"]),
            "event_name": ["near", "far", "closer"],
        }
    )
    change_date = pd.Timestamp("2020-01-05")
    result = nearest_events(change_date, events, window_days=30, top_n=2)

    assert list(result["event_name"]) == ["near", "closer"]
    assert result["within_window"].all()
