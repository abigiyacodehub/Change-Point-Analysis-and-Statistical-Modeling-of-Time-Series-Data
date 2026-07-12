"""Data loading utilities for Brent oil price and event datasets.

These functions centralize file I/O and basic validation so notebooks and
scripts do not duplicate parsing logic, and so common failure modes (missing
files, malformed rows) raise clear, actionable errors instead of failing
deep inside pandas with a cryptic traceback.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

DEFAULT_PRICE_PATH = os.path.join("data", "raw", "BrentOilPrices.csv")
DEFAULT_EVENTS_PATH = os.path.join("data", "events", "key_events.csv")


class DataLoadError(RuntimeError):
    """Raised when a dataset cannot be loaded or fails validation."""


@dataclass(frozen=True)
class LoadedSeries:
    """Container bundling the raw price frame with derived columns."""

    prices: pd.DataFrame
    log_returns: pd.Series


def load_brent_prices(path: str = DEFAULT_PRICE_PATH) -> pd.DataFrame:
    """Load the Brent oil price series from a CSV file.

    Expects two columns: ``Date`` (parseable date) and ``Price`` (float,
    USD per barrel). Rows with missing/non-numeric prices are dropped.

    Raises:
        DataLoadError: if the file is missing, empty, or missing required
            columns.
    """
    if not os.path.exists(path):
        raise DataLoadError(
            f"Brent price file not found at '{path}'. "
            "Run `python scripts/download_data.py` to fetch it first."
        )

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise DataLoadError(f"Price file '{path}' is empty.") from exc
    except pd.errors.ParserError as exc:
        raise DataLoadError(f"Price file '{path}' could not be parsed as CSV: {exc}") from exc

    required_columns = {"Date", "Price"}
    missing = required_columns - set(df.columns)
    if missing:
        raise DataLoadError(
            f"Price file '{path}' is missing required column(s): {sorted(missing)}"
        )

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")

    n_before = len(df)
    df = df.dropna(subset=["Date", "Price"]).copy()
    n_dropped = n_before - len(df)
    if n_dropped:
        # Not fatal: weekends/holidays and the occasional "." placeholder
        # value are expected in raw market data feeds.
        pass

    if df.empty:
        raise DataLoadError(f"Price file '{path}' contained no valid rows after cleaning.")

    df = df.sort_values("Date").reset_index(drop=True)
    return df


def compute_log_returns(prices: pd.DataFrame, price_col: str = "Price") -> pd.Series:
    """Compute log returns from a price column.

    Raises:
        DataLoadError: if the price column is missing or has fewer than
            two valid observations.
    """
    if price_col not in prices.columns:
        raise DataLoadError(f"Column '{price_col}' not found for log return computation.")

    series = prices[price_col].astype(float)
    if len(series) < 2:
        raise DataLoadError("Need at least two price observations to compute log returns.")

    log_returns = np.log(series / series.shift(1))
    return log_returns.rename("LogReturn")


def load_brent_series(path: str = DEFAULT_PRICE_PATH) -> LoadedSeries:
    """Convenience loader returning both the price frame and its log returns."""
    prices = load_brent_prices(path)
    log_returns = compute_log_returns(prices)
    return LoadedSeries(prices=prices, log_returns=log_returns)


def load_key_events(path: str = DEFAULT_EVENTS_PATH) -> pd.DataFrame:
    """Load the structured key-events dataset (geopolitical/OPEC/economic).

    Raises:
        DataLoadError: if the file is missing or missing required columns.
    """
    if not os.path.exists(path):
        raise DataLoadError(f"Events file not found at '{path}'.")

    try:
        df = pd.read_csv(path)
    except pd.errors.EmptyDataError as exc:
        raise DataLoadError(f"Events file '{path}' is empty.") from exc

    required_columns = {"event_id", "date", "event_name", "category"}
    missing = required_columns - set(df.columns)
    if missing:
        raise DataLoadError(
            f"Events file '{path}' is missing required column(s): {sorted(missing)}"
        )

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if df["date"].isna().any():
        bad_rows = df[df["date"].isna()]["event_id"].tolist()
        raise DataLoadError(f"Events file '{path}' has unparseable dates for event_id(s): {bad_rows}")

    return df.sort_values("date").reset_index(drop=True)
