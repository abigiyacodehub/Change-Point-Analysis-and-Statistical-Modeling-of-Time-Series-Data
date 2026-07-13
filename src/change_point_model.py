"""Bayesian single change point model for the Brent log-return series.

Implements the classic switch-point formulation: an unknown index ``tau``
splits the series into a "before" and "after" regime, each with its own
mean and volatility, connected by ``pm.math.switch``. This lets the model
answer "when did the statistical behavior of returns shift, and how did
the mean/volatility level change?" without the analyst specifying the
date in advance.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pymc as pm


class ChangePointModelError(RuntimeError):
    """Raised when the change point model cannot be built or fit."""


@dataclass(frozen=True)
class ChangePointFit:
    """Container bundling the fitted PyMC model with its trace and inputs."""

    model: pm.Model
    trace: object  # arviz.InferenceData
    dates: pd.Series
    values: np.ndarray


def build_change_point_model(values: np.ndarray) -> pm.Model:
    """Build (but do not sample) a single change point model.

    Parameters
    ----------
    values:
        1-D array of observations (e.g., daily log returns) with no NaNs.

    Returns
    -------
    A PyMC model with random variables ``tau`` (discrete switch index),
    ``mu1``/``mu2`` (before/after means), ``sigma1``/``sigma2``
    (before/after standard deviations), and observed likelihood ``obs``.

    Raises
    ------
    ChangePointModelError: if ``values`` is empty, contains NaNs, or is
        too short to plausibly contain a change point.
    """
    if values.ndim != 1:
        raise ChangePointModelError("values must be a 1-D array.")
    if len(values) < 30:
        raise ChangePointModelError(
            f"Need at least 30 observations to fit a change point model, got {len(values)}."
        )
    if np.isnan(values).any():
        raise ChangePointModelError("values must not contain NaNs; drop or impute them first.")

    n = len(values)
    idx = np.arange(n)
    scale = float(np.std(values)) or 1.0

    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

        mu1 = pm.Normal("mu1", mu=0.0, sigma=scale)
        mu2 = pm.Normal("mu2", mu=0.0, sigma=scale)
        sigma1 = pm.HalfNormal("sigma1", sigma=scale)
        sigma2 = pm.HalfNormal("sigma2", sigma=scale)

        mu = pm.math.switch(tau >= idx, mu1, mu2)
        sigma = pm.math.switch(tau >= idx, sigma1, sigma2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=values)

    return model


def fit_change_point_model(
    dates: pd.Series,
    values: np.ndarray,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    cores: int = 4,
    random_seed: int = 42,
    target_accept: float = 0.9,
) -> ChangePointFit:
    """Build the change point model and run MCMC sampling via ``pm.sample``.

    Raises
    ------
    ChangePointModelError: if ``dates`` and ``values`` have mismatched
        lengths, or model construction fails (see :func:`build_change_point_model`).
    """
    if len(dates) != len(values):
        raise ChangePointModelError(
            f"dates (len={len(dates)}) and values (len={len(values)}) must be the same length."
        )

    model = build_change_point_model(np.asarray(values, dtype=float))

    with model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=cores,
            random_seed=random_seed,
            target_accept=target_accept,
            progressbar=False,
        )

    return ChangePointFit(
        model=model,
        trace=trace,
        dates=pd.Series(dates).reset_index(drop=True),
        values=np.asarray(values, dtype=float),
    )


def nearest_events(
    change_date: pd.Timestamp,
    events: pd.DataFrame,
    window_days: int = 90,
    top_n: int = 3,
) -> pd.DataFrame:
    """Return the ``top_n`` events closest in time to ``change_date``.

    Only events within ``window_days`` are considered "plausibly linked";
    events outside that window are still returned (for context) but the
    caller should treat them as weak candidates. Distance is measured in
    absolute days.

    Raises
    ------
    ChangePointModelError: if ``events`` is missing a ``date`` column.
    """
    if "date" not in events.columns:
        raise ChangePointModelError("events frame must have a 'date' column.")

    ev = events.copy()
    ev["days_from_change_point"] = (ev["date"] - change_date).dt.days
    ev["abs_days"] = ev["days_from_change_point"].abs()
    ev = ev.sort_values("abs_days").head(top_n)
    ev["within_window"] = ev["abs_days"] <= window_days
    return ev.drop(columns=["abs_days"])
