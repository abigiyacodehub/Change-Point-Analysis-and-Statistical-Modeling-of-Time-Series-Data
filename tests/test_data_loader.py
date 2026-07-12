"""Unit tests for src.data_loader.

Run with: pytest tests/
"""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data_loader import (
    DataLoadError,
    compute_log_returns,
    load_brent_prices,
    load_key_events,
)


@pytest.fixture
def tmp_price_csv(tmp_path):
    df = pd.DataFrame(
        {
            "Date": ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"],
            "Price": [66.0, 66.5, ".", 65.0],
        }
    )
    path = tmp_path / "prices.csv"
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def tmp_events_csv(tmp_path):
    df = pd.DataFrame(
        {
            "event_id": [1, 2],
            "date": ["2020-01-01", "2020-01-02"],
            "event_name": ["Test event A", "Test event B"],
            "category": ["Geopolitical", "OPEC"],
        }
    )
    path = tmp_path / "events.csv"
    df.to_csv(path, index=False)
    return str(path)


def test_load_brent_prices_missing_file():
    with pytest.raises(DataLoadError):
        load_brent_prices("does/not/exist.csv")


def test_load_brent_prices_drops_invalid_rows(tmp_price_csv):
    df = load_brent_prices(tmp_price_csv)
    # The "." price row should be dropped, leaving 3 valid rows.
    assert len(df) == 3
    assert list(df.columns) == ["Date", "Price"]
    assert df["Price"].dtype == float


def test_load_brent_prices_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"Date": ["2020-01-01"]}).to_csv(bad, index=False)
    with pytest.raises(DataLoadError):
        load_brent_prices(str(bad))


def test_compute_log_returns():
    prices = pd.DataFrame({"Price": [100.0, 110.0, 99.0]})
    log_returns = compute_log_returns(prices)
    assert np.isnan(log_returns.iloc[0])
    assert log_returns.iloc[1] == pytest.approx(np.log(110.0 / 100.0))
    assert log_returns.iloc[2] == pytest.approx(np.log(99.0 / 110.0))


def test_compute_log_returns_missing_column():
    with pytest.raises(DataLoadError):
        compute_log_returns(pd.DataFrame({"NotPrice": [1, 2, 3]}))


def test_load_key_events(tmp_events_csv):
    df = load_key_events(tmp_events_csv)
    assert len(df) == 2
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_key_events_missing_file():
    with pytest.raises(DataLoadError):
        load_key_events("nope.csv")
