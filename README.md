# Change Point Analysis and Statistical Modeling of Brent Oil Prices

Analyzing how major geopolitical events, OPEC decisions, and macroeconomic
shocks relate to structural changes ("change points") in the price of Brent
crude oil, using time series EDA and change point detection.

## Project status

This is an interim submission covering:

- **Task 1a** — analysis workflow plan, a structured dataset of key
  geopolitical/OPEC/economic events, and documented assumptions/limitations.
- **Task 1b** — exploratory data analysis of the Brent oil price series
  (raw price and log returns), trend/stationarity/volatility investigation,
  and a written explanation of change point models.

Change point modeling itself (fitting the model, reporting detected change
points, and comparing them against the event dataset) is planned for the
next phase of the project.

## Data source

- **Brent crude oil price**: `data/raw/BrentOilPrices.csv` — daily "Crude
  Oil Prices: Brent - Europe" series (FRED code `DCOILBRENTEU`), covering
  1987 to present. Refresh it with `python scripts/download_data.py`.
- **Key events**: `data/events/key_events.csv` — a hand-compiled dataset of
  20 major geopolitical, OPEC/OPEC+, and macroeconomic events with
  approximate dates, categories, and descriptions.

## Project structure

```
.
├── data/
│   ├── raw/BrentOilPrices.csv     # Brent oil price series (Date, Price)
│   └── events/key_events.csv      # Structured event dataset
├── docs/
│   ├── analysis_workflow.md       # Task 1a: planned analysis workflow
│   └── assumptions_and_limitations.md
├── notebooks/
│   └── 01_eda_and_change_point_understanding.ipynb  # Task 1b: EDA notebook
├── scripts/
│   └── download_data.py           # Refresh the Brent price dataset from FRED
├── src/
│   ├── data_loader.py             # Data loading/validation helpers
│   └── eda.py                     # Stationarity, volatility, plotting helpers
├── tests/
│   └── test_data_loader.py        # Unit tests for src/data_loader.py
├── requirements.txt
└── .gitignore
```

## Setup

```bash
pip install -r requirements.txt
```

## Running things

- **Refresh the price data**: `python scripts/download_data.py`
- **Run the EDA notebook**: `jupyter notebook notebooks/01_eda_and_change_point_understanding.ipynb`
- **Run unit tests**: `pytest tests/`

## Key findings so far (Task 1b)

- The raw Brent price series is non-stationary (confirmed via the Augmented
  Dickey-Fuller test), showing multi-year trending regimes rather than
  fluctuation around a constant mean.
- Daily log returns are approximately stationary and better suited to
  change point / volatility modeling.
- Volatility is not constant over time ("volatility clustering") — periods
  of large price swings cluster around known crisis periods (e.g., 2008-2009,
  2014-2016, 2020), motivating a change point approach that can detect
  shifts in variance, not just in mean.

See `notebooks/01_eda_and_change_point_understanding.ipynb` for the full
analysis, and `docs/assumptions_and_limitations.md` for an important
discussion of why temporal proximity between an event and a detected change
point is an association, not proof of causation.
