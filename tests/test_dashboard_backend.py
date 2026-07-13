"""Tests for the Flask API in dashboard/backend/app.py.

Uses Flask's test client (no real network/server needed) and exercises
both the happy paths and the documented error-handling behavior.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dashboard", "backend")))

from app import app as flask_app  # noqa: E402


@pytest.fixture()
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}


def test_prices_returns_data(client):
    resp = client.get("/api/prices")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] > 0
    assert set(body["data"][0].keys()) == {"date", "price", "log_return"}


def test_prices_date_range_filters_results(client):
    resp = client.get("/api/prices?start=2020-01-01&end=2020-01-10")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] > 0
    for row in body["data"]:
        assert "2020-01-01" <= row["date"] <= "2020-01-10"


def test_prices_invalid_date_returns_400(client):
    resp = client.get("/api/prices?start=not-a-date")
    assert resp.status_code == 400
    assert "error" in resp.get_json()


def test_prices_start_after_end_returns_400(client):
    resp = client.get("/api/prices?start=2020-06-01&end=2020-01-01")
    assert resp.status_code == 400


def test_change_points_returns_expected_shape(client):
    resp = client.get("/api/change-points")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "change_point_date" in body
    assert "linked_events" in body


def test_change_points_missing_file_returns_503(client, tmp_path, monkeypatch):
    import app as app_module

    missing_path = tmp_path / "does_not_exist.json"
    monkeypatch.setattr(app_module, "CHANGE_POINT_RESULTS_PATH", str(missing_path))

    resp = client.get("/api/change-points")
    assert resp.status_code == 503


def test_events_returns_data(client):
    resp = client.get("/api/events")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] >= 10
    assert "event_name" in body["data"][0]


def test_events_category_filter(client):
    resp = client.get("/api/events?category=opec")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["count"] > 0
    assert all(row["category"].lower() == "opec" for row in body["data"])


def test_unknown_route_returns_404(client):
    resp = client.get("/api/does-not-exist")
    assert resp.status_code == 404
