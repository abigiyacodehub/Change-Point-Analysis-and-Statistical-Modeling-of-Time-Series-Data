"""Unit tests for scripts.download_data (network calls are mocked)."""

import os
import sys

import pandas as pd
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.download_data import clean_and_save, fetch_brent_csv


class _FakeResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text


def test_fetch_brent_csv_network_error(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("boom")

    monkeypatch.setattr(requests, "get", raise_connection_error)
    with pytest.raises(RuntimeError):
        fetch_brent_csv()


def test_fetch_brent_csv_non_200(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(status_code=503))
    with pytest.raises(RuntimeError):
        fetch_brent_csv()


def test_fetch_brent_csv_empty_payload(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *a, **k: _FakeResponse(text=""))
    with pytest.raises(RuntimeError):
        fetch_brent_csv()


def test_clean_and_save_no_valid_rows(tmp_path):
    raw = pd.DataFrame({"observation_date": [".", "."], "DCOILBRENTEU": [".", "."]})
    out = tmp_path / "out.csv"
    with pytest.raises(RuntimeError):
        clean_and_save(raw, output_path=str(out))


def test_clean_and_save_writes_expected_rows(tmp_path):
    raw = pd.DataFrame(
        {
            "observation_date": ["2020-01-01", "2020-01-02", "2020-01-03"],
            "DCOILBRENTEU": ["66.0", ".", "65.5"],
        }
    )
    out = tmp_path / "out.csv"
    n_rows = clean_and_save(raw, output_path=str(out))
    assert n_rows == 2
    saved = pd.read_csv(out)
    assert list(saved.columns) == ["Date", "Price"]
