"""Reusable EDA helpers: stationarity tests, rolling volatility, plotting.

Keeping these as functions (rather than inline notebook code) makes the
notebook readable and lets the same logic be unit tested.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller


def adf_test(series: pd.Series, name: str = "series") -> dict:
    """Run an Augmented Dickey-Fuller stationarity test.

    Returns a dict with the test statistic, p-value, and a plain-language
    verdict at the 5% significance level. Raises ValueError if the series
    has too few observations for the test to run.
    """
    clean = series.dropna()
    if len(clean) < 10:
        raise ValueError(
            f"'{name}' has only {len(clean)} non-null observations; "
            "need at least 10 for a meaningful ADF test."
        )

    result = adfuller(clean, autolag="AIC")
    stat, p_value = result[0], result[1]
    return {
        "name": name,
        "adf_statistic": stat,
        "p_value": p_value,
        "n_obs": int(result[3]),
        "is_stationary_at_5pct": bool(p_value < 0.05),
    }


def rolling_volatility(log_returns: pd.Series, window: int = 30) -> pd.Series:
    """Rolling standard deviation of log returns, annualized-free (raw daily units)."""
    if window < 2:
        raise ValueError("window must be >= 2")
    return log_returns.rolling(window=window, min_periods=window // 2).std().rename(
        f"RollingVol_{window}d"
    )


def plot_price_series(
    prices: pd.DataFrame,
    date_col: str = "Date",
    price_col: str = "Price",
    title: str = "Brent Crude Oil Price (USD/barrel)",
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot the raw price series over time."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(prices[date_col], prices[price_col], linewidth=0.8, color="#1f4e79")
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("USD per barrel")
    ax.grid(alpha=0.3)
    return ax


def plot_log_returns(
    dates: pd.Series,
    log_returns: pd.Series,
    title: str = "Brent Crude Oil Daily Log Returns",
    ax: Optional[plt.Axes] = None,
) -> plt.Axes:
    """Plot the log-return series over time."""
    if ax is None:
        _, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(dates, log_returns, linewidth=0.5, color="#a63d40")
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Log return")
    ax.grid(alpha=0.3)
    return ax
