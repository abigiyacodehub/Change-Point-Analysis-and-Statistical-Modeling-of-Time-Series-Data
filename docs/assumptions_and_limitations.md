# Assumptions and Limitations

## Assumptions

1. **Data quality**: The Brent oil price series (sourced from FRED,
   series `DCOILBRENTEU`) is assumed to be accurate and representative of
   spot market prices. Missing values (market holidays/weekends) are dropped
   rather than imputed, since oil markets are simply closed on those days.
2. **Event dates are approximate**: Dates in `data/events/key_events.csv`
   represent the most commonly cited date for the start or announcement of
   an event (e.g., an invasion date, an OPEC meeting decision date). Real-world
   market reactions can begin before an event (anticipation/rumor) or persist
   for weeks afterward, so "the" date is a simplification of a more gradual
   process.
3. **Log returns approximate a stationary process**: We assume that,
   unlike the raw price level, log returns are closer to a stationary,
   mean-reverting series suitable for volatility and change point analysis.
   This is a standard assumption in financial time series analysis but is
   not guaranteed to hold perfectly across all sub-periods (e.g., during
   extreme events).
4. **A single global oil price is a reasonable simplification**: Brent
   crude is used as the global benchmark, but actual regional prices
   (e.g., WTI, OPEC basket, local blends) can diverge from Brent due to
   transport costs, quality differentials, and regional supply/demand
   imbalances.
5. **Change points reflect structural shifts, not noise**: We assume that
   sufficiently large and persistent shifts in mean or variance identified
   by change point models reflect genuine regime changes rather than
   short-lived noise, though the threshold for "sufficiently large" is a
   modeling choice.

## Limitations

1. **Correlation in time is not causation.** This is the most important
   limitation of this analysis. A change point detected in the price series
   occurring near the date of a geopolitical or OPEC event does **not**
   prove that the event caused the price shift. Oil prices are influenced
   by many simultaneous factors (macroeconomic data releases, currency
   movements, weather, unrelated supply disruptions, speculative trading
   flows, etc.), and apparent temporal alignment between an event and a
   change point can be coincidental. Establishing causality would require
   a counterfactual analysis (what would have happened without the event),
   which is outside the scope of a purely observational change point study.
2. **Multiple plausible events per change point.** Because major
   geopolitical and economic events often cluster in time, a single
   detected change point may be temporally close to more than one candidate
   event, making it hard to attribute the shift to a single cause.
3. **Sensitivity to model choice.** Different change point detection
   methods (e.g., Bayesian change point models vs. PELT/binary segmentation)
   and different hyperparameters (e.g., penalty terms, expected number of
   change points) can produce different sets of detected change points from
   the same data.
4. **Survivorship of narrative bias.** The event dataset was compiled based
   on well-documented, widely reported historical events. Smaller or less
   publicized supply/demand shocks that also affected prices are likely
   underrepresented.
5. **No adjustment for inflation or currency effects.** Prices are analyzed
   in nominal USD terms; long-run comparisons across decades do not account
   for inflation, which can affect the interpretation of "large" price
   moves in early vs. recent history.
6. **Lookback bias in event selection.** Events were chosen partly because
   they are known, in hindsight, to have been significant to oil markets.
   This differs from a forward-looking analysis that would need to identify
   the importance of events without hindsight.
