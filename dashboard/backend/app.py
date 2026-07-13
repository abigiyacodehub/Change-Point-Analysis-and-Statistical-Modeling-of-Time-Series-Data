"""Flask API for the Brent oil change point dashboard (Task 3).

Serves three read-only endpoints for the React frontend:

- ``GET /api/prices``          historical Brent price series (raw + log return)
- ``GET /api/change-points``   Bayesian change point model results (Task 2)
- ``GET /api/events``          structured key events dataset (Task 1)

All three support an optional ``start``/``end`` (YYYY-MM-DD) date-range
filter so the frontend can narrow the view without re-fetching everything.

Run with: ``python dashboard/backend/app.py`` (see dashboard/README.md).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# Make the repo root importable regardless of the current working directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.data_loader import DataLoadError, load_brent_series, load_key_events  # noqa: E402

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHANGE_POINT_RESULTS_PATH = os.path.join(REPO_ROOT, "data", "processed", "change_point_results.json")

app = Flask(__name__)
CORS(app)


class ApiError(RuntimeError):
    """Raised for client-facing API errors (mapped to 4xx responses)."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@app.errorhandler(ApiError)
def handle_api_error(err: ApiError):
    return jsonify({"error": err.message}), err.status_code


@app.errorhandler(404)
def handle_not_found(_err):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def handle_internal_error(_err):
    return jsonify({"error": "Internal server error"}), 500


def _parse_date_param(name: str) -> "datetime | None":
    raw = request.args.get(name)
    if raw is None or raw == "":
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except ValueError as exc:
        raise ApiError(f"Invalid '{name}' date '{raw}'; expected YYYY-MM-DD.") from exc


def _date_range_from_request() -> tuple:
    start = _parse_date_param("start")
    end = _parse_date_param("end")
    if start and end and start > end:
        raise ApiError("'start' date must not be after 'end' date.")
    return start, end


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/prices")
def get_prices():
    """Historical Brent prices and log returns, optionally filtered by date range."""
    start, end = _date_range_from_request()

    try:
        series = load_brent_series()
    except DataLoadError as exc:
        raise ApiError(str(exc), status_code=503) from exc

    prices = series.prices.copy()
    prices["LogReturn"] = series.log_returns

    if start is not None:
        prices = prices[prices["Date"] >= start]
    if end is not None:
        prices = prices[prices["Date"] <= end]

    records = [
        {
            "date": row.Date.strftime("%Y-%m-%d"),
            "price": None if row.Price != row.Price else round(float(row.Price), 4),
            "log_return": None if row.LogReturn != row.LogReturn else round(float(row.LogReturn), 6),
        }
        for row in prices.itertuples(index=False)
    ]
    return jsonify({"count": len(records), "data": records})


@app.get("/api/change-points")
def get_change_points():
    """Bayesian change point model results produced by notebook 02."""
    if not os.path.exists(CHANGE_POINT_RESULTS_PATH):
        raise ApiError(
            "Change point results not found. Run "
            "notebooks/02_bayesian_change_point_model.ipynb first to generate "
            "data/processed/change_point_results.json.",
            status_code=503,
        )

    try:
        with open(CHANGE_POINT_RESULTS_PATH) as f:
            results = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        raise ApiError(f"Could not read change point results: {exc}", status_code=500) from exc

    return jsonify(results)


@app.get("/api/events")
def get_events():
    """Structured key events dataset, optionally filtered by date range and category."""
    start, end = _date_range_from_request()
    category = request.args.get("category")

    try:
        events = load_key_events()
    except DataLoadError as exc:
        raise ApiError(str(exc), status_code=503) from exc

    if start is not None:
        events = events[events["date"] >= start]
    if end is not None:
        events = events[events["date"] <= end]
    if category:
        events = events[events["category"].str.lower() == category.lower()]

    records = json.loads(
        events.assign(date=events["date"].dt.strftime("%Y-%m-%d")).to_json(orient="records")
    )
    return jsonify({"count": len(records), "data": records})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
