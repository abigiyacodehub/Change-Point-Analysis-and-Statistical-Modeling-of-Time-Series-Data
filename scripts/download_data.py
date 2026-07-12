#!/usr/bin/env python
"""Download and refresh the Brent oil price dataset from FRED.

Usage:
    python scripts/download_data.py

Fetches the "Crude Oil Prices: Brent - Europe" daily series
(FRED code DCOILBRENTEU) and writes a cleaned Date/Price CSV to
data/raw/BrentOilPrices.csv. Includes basic error handling for
network failures and malformed responses so the failure mode is
clear instead of a raw stack trace deep inside pandas/requests.
"""

from __future__ import annotations

import io
import os
import sys

import pandas as pd
import requests

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"
OUTPUT_PATH = os.path.join("data", "raw", "BrentOilPrices.csv")


def fetch_brent_csv(url: str = FRED_URL, timeout: int = 30) -> pd.DataFrame:
    """Fetch the raw FRED CSV and return it as a DataFrame.

    Raises:
        RuntimeError: on network failure, non-200 response, or an
            unparseable/empty payload.
    """
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to reach FRED at '{url}': {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"FRED returned HTTP {response.status_code} when fetching '{url}'."
        )

    try:
        df = pd.read_csv(io.StringIO(response.text))
    except pd.errors.ParserError as exc:
        raise RuntimeError(f"Could not parse FRED response as CSV: {exc}") from exc

    if df.empty or df.shape[1] < 2:
        raise RuntimeError("FRED response did not contain the expected two columns.")

    return df


def clean_and_save(raw_df: pd.DataFrame, output_path: str = OUTPUT_PATH) -> int:
    """Clean the raw FRED frame to Date/Price columns and write to disk.

    Returns the number of rows written. Raises RuntimeError if no valid
    rows remain after cleaning.
    """
    date_col, price_col = raw_df.columns[0], raw_df.columns[1]
    cleaned = raw_df.rename(columns={date_col: "Date", price_col: "Price"})
    cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
    cleaned = cleaned.dropna(subset=["Price"]).copy()

    if cleaned.empty:
        raise RuntimeError("No valid price rows remained after cleaning FRED data.")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cleaned.to_csv(output_path, index=False)
    return len(cleaned)


def main() -> int:
    try:
        raw_df = fetch_brent_csv()
        n_rows = clean_and_save(raw_df)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Saved {n_rows} rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
