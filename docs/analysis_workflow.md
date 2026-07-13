# Analysis Workflow: Change Point Analysis of Brent Oil Prices

## Objective

Investigate how major geopolitical, OPEC, and macroeconomic events are
associated with structural changes (change points) in the price of Brent
crude oil, and communicate the results to stakeholders (investors, policy
analysts, energy companies) who need to understand price regime shifts.

## Planned Steps

1. **Data acquisition**
   - Load the historical Brent oil price series (`data/raw/BrentOilPrices.csv`,
     daily observations from 1987 to present, sourced from FRED series
     `DCOILBRENTEU`).
   - Compile a structured dataset of major events (`data/events/key_events.csv`)
     covering geopolitical shocks, OPEC/OPEC+ decisions, and macroeconomic
     crises, each with an approximate date and category.

2. **Data cleaning and preparation**
   - Parse dates, sort chronologically, and check for duplicates or gaps
     (the series is missing weekends/holidays, which is expected for a
     trading price series).
   - Compute log returns (`log(P_t / P_{t-1})`) as the primary series for
     change point and volatility analysis, since raw prices are non-stationary.

3. **Exploratory Data Analysis (EDA)**
   - Plot the raw price series and log-return series over the full history.
   - Examine trend behavior, rolling mean/volatility, and long-run regimes.
   - Run stationarity diagnostics (Augmented Dickey-Fuller test) on both the
     raw price and the log-return series.
   - Visually and statistically assess volatility clustering (periods of
     calm vs. turbulent prices).

4. **Change point model understanding**
   - Explain the purpose of change point detection models (e.g., Bayesian
     change point models, PELT/`ruptures`-based methods) for identifying
     structural breaks in the mean, variance, or trend of the price series.
   - Describe expected outputs: change point dates/date ranges, pre- and
     post-change parameter estimates (mean, volatility), and credible
     intervals or confidence measures around detected change points.

5. **Event-to-change-point comparison (subsequent phase)**
   - Overlay detected change points against the compiled event dataset to
     look for temporal proximity between structural breaks and known events.
   - Report associations descriptively, respecting the assumptions and
     limitations documented separately (see
     `docs/assumptions_and_limitations.md`).

6. **Insight generation and communication (subsequent phase)**
   - Summarize which events most plausibly coincide with detected regime
     shifts, quantify the change in price level/volatility around each
     change point, and prepare a stakeholder-facing summary (report/dashboard)
     of findings.

6. **Interactive dashboard (subsequent phase)**
   - Serve the price series, detected change point(s), and event dataset
     through a Flask API and a React frontend so stakeholders can explore
     the analysis interactively (date range filtering, event highlighting)
     without reading the notebooks directly.

## Deliverables

- This workflow document.
- The structured event dataset (`data/events/key_events.csv`).
- The assumptions and limitations document (`docs/assumptions_and_limitations.md`).
- An EDA notebook (`notebooks/01_eda_and_change_point_understanding.ipynb`)
  covering raw price/log-return visualization, stationarity/volatility
  analysis, and a written explanation of change point models.
- A Bayesian change point model notebook
  (`notebooks/02_bayesian_change_point_model.ipynb`) implementing steps 4-5:
  a PyMC single change point model with MCMC sampling, convergence
  diagnostics, and an interpretation linking the detected change point to
  the compiled event dataset.
- An interactive Flask/React dashboard (`dashboard/`) implementing step 6.
