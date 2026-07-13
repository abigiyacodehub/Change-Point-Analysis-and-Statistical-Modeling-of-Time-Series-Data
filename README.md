# Change Point Analysis and Statistical Modeling of Brent Oil Prices

Analyzing how major geopolitical events, OPEC decisions, and macroeconomic
shocks relate to structural changes ("change points") in the price of Brent
crude oil, using time series EDA and change point detection.

## Project status

- **Task 1** — analysis workflow plan, a structured dataset of 20 key
  geopolitical/OPEC/economic events, documented assumptions/limitations, and
  exploratory data analysis of the Brent oil price series (raw price and log
  returns) with trend/stationarity/volatility investigation.
- **Task 2** — a Bayesian single change point model (PyMC), fit via MCMC
  sampling with convergence diagnostics, interpreting the detected change
  point against the compiled event dataset.
- **Task 3** — an interactive Flask/React dashboard (`dashboard/`) for
  stakeholders to explore the price series, the detected change point, and
  event correlations with date-range and category filtering.

## Data source

- **Brent crude oil price**: `data/raw/BrentOilPrices.csv` — daily "Crude
  Oil Prices: Brent - Europe" series (FRED code `DCOILBRENTEU`), covering
  1987 to present. Refresh it with `python scripts/download_data.py`.
- **Key events**: `data/events/key_events.csv` — a hand-compiled dataset of
  20 major geopolitical, OPEC/OPEC+, and macroeconomic events with
  approximate dates, categories, and descriptions.

## Project structure

This repository contains only the change-point analysis project. All paths
below are top-level; `src/`, `notebooks/`, `scripts/`, and `tests/` are not
nested under anything else, so the analysis can be reproduced directly from
a fresh clone with no other setup.

```
.
├── data/
│   ├── raw/BrentOilPrices.csv       # Brent oil price series (Date, Price)
│   ├── events/key_events.csv        # Structured event dataset (20 events)
│   └── processed/change_point_results.json  # Task 2 model output (dashboard input)
├── docs/
│   ├── analysis_workflow.md         # Task 1: planned analysis workflow
│   └── assumptions_and_limitations.md
├── notebooks/
│   ├── 01_eda_and_change_point_understanding.ipynb  # Task 1: EDA notebook
│   └── 02_bayesian_change_point_model.ipynb         # Task 2: PyMC model notebook
├── scripts/
│   └── download_data.py             # Refresh the Brent price dataset from FRED
├── src/
│   ├── __init__.py
│   ├── data_loader.py               # Data loading/validation helpers
│   ├── eda.py                       # Stationarity, volatility, plotting helpers
│   └── change_point_model.py        # Task 2: PyMC change point model
├── dashboard/
│   ├── backend/app.py                # Task 3: Flask API (prices, change points, events)
│   └── frontend/                     # Task 3: React dashboard UI
├── docs/screenshots/                 # Task 3: dashboard screenshots
├── tests/
│   ├── test_data_loader.py          # Unit tests for src/data_loader.py
│   ├── test_eda.py                  # Unit tests for src/eda.py
│   ├── test_change_point_model.py   # Unit tests for src/change_point_model.py
│   └── test_download_data.py        # Unit tests for scripts/download_data.py
├── .github/workflows/unittests.yml  # CI: run pytest on every push/PR
├── requirements.txt                  # Root-level, pip-installable dependency list
└── .gitignore
```

## Setup

```bash
pip install -r requirements.txt
```

## Running things

- **Refresh the price data**: `python scripts/download_data.py`
- **Run the EDA notebook**: `jupyter notebook notebooks/01_eda_and_change_point_understanding.ipynb`
- **Run the change point model notebook**: `jupyter notebook notebooks/02_bayesian_change_point_model.ipynb`
  (fits the PyMC model via MCMC and rewrites `data/processed/change_point_results.json`)
- **Run unit tests**: `pytest tests/` (covers `src/data_loader.py`, `src/eda.py`,
  `src/change_point_model.py`, and `scripts/download_data.py`, including error
  paths such as missing files, malformed rows, and network failures)
- **Run the dashboard**: see `dashboard/README.md` for backend + frontend setup

## Key findings

- The raw Brent price series is non-stationary (confirmed via the Augmented
  Dickey-Fuller test), showing multi-year trending regimes rather than
  fluctuation around a constant mean.
- Daily log returns are approximately stationary and better suited to
  change point / volatility modeling.
- Volatility is not constant over time ("volatility clustering") — periods
  of large price swings cluster around known crisis periods (e.g., 2008-2009,
  2014-2016, 2020), motivating a change point approach that can detect
  shifts in variance, not just in mean.
- A Bayesian single change point model (`src/change_point_model.py`, fit in
  `notebooks/02_bayesian_change_point_model.ipynb`) detects its dominant
  regime shift around **2008-07-29** (95% credible interval spans roughly
  May-September 2008), with volatility rising ~20% after the change point.
  This lands within 90 days of two compiled events: Brent's July 2008 price
  peak and the September 2008 Global Financial Crisis / Lehman Brothers
  collapse.

See `notebooks/01_eda_and_change_point_understanding.ipynb` and
`notebooks/02_bayesian_change_point_model.ipynb` for the full analysis, and
`docs/assumptions_and_limitations.md` for an important discussion of why
temporal proximity between an event and a detected change point is an
association, not proof of causation.
