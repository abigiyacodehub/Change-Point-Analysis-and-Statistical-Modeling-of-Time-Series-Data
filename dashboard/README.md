# Brent Oil Change Point Dashboard (Task 3)

An interactive dashboard that lets stakeholders explore Brent oil prices,
the Bayesian change point detected in Task 2, and the compiled event
dataset from Task 1 — without reading the notebooks directly.

- **Backend**: Flask API (`backend/app.py`) serving prices, change point
  results, and events as JSON, with date-range and category filtering.
- **Frontend**: React + Vite app (`frontend/`) rendering an interactive
  price chart (Recharts) with the change point's credible interval and
  linked events highlighted, plus a filterable event list.

See `docs/screenshots/dashboard_overview.png` in the repo root for a
screenshot of the running dashboard.

## Prerequisites

- The repo's root Python dependencies installed: `pip install -r ../requirements.txt`
  (from the repo root: `pip install -r requirements.txt`)
- `data/processed/change_point_results.json` present — already committed,
  but you can regenerate it by re-running
  `notebooks/02_bayesian_change_point_model.ipynb`.
- Node.js 18+ and npm for the frontend.

## Running the backend

From the repository root:

```bash
python dashboard/backend/app.py
```

This starts the Flask API on `http://localhost:5001` (override with the
`PORT` environment variable). Endpoints:

- `GET /api/health` — liveness check
- `GET /api/prices?start=YYYY-MM-DD&end=YYYY-MM-DD` — price series + log returns
- `GET /api/change-points` — Bayesian change point model results
- `GET /api/events?start=YYYY-MM-DD&end=YYYY-MM-DD&category=OPEC` — key events

## Running the frontend

```bash
cd dashboard/frontend
npm install
npm run dev
```

This starts the Vite dev server on `http://localhost:5173`. By default it
talks to the backend at `http://localhost:5001`; override with
`VITE_API_BASE_URL` if the backend runs elsewhere, e.g.:

```bash
VITE_API_BASE_URL=http://localhost:5001 npm run dev
```

Open `http://localhost:5173` in a browser once both processes are running.

## Running tests

Backend tests live alongside the rest of the project's test suite and run
with the same command from the repo root:

```bash
pytest tests/test_dashboard_backend.py
```

## Error handling

The API returns structured `{"error": "..."}` JSON with an appropriate
HTTP status code for invalid input (e.g. malformed dates, `start` after
`end`) and for missing upstream data (e.g. `data/processed/change_point_results.json`
not yet generated), rather than raising uncaught exceptions. The frontend
surfaces these messages in an error banner instead of failing silently.
