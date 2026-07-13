import { useEffect, useMemo, useState } from "react";
import PriceChart from "./components/PriceChart.jsx";
import EventList from "./components/EventList.jsx";
import DateRangeFilter from "./components/DateRangeFilter.jsx";
import { ApiRequestError, fetchChangePoints, fetchEvents, fetchPrices } from "./api.js";

const DEFAULT_START = "2005-01-01";
const DEFAULT_END = "2012-12-31";

export default function App() {
  const [start, setStart] = useState(DEFAULT_START);
  const [end, setEnd] = useState(DEFAULT_END);
  const [category, setCategory] = useState("");

  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoint, setChangePoint] = useState(null);
  const [allEventCategories, setAllEventCategories] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Change point results don't depend on the date filter; load once.
  useEffect(() => {
    fetchChangePoints()
      .then(setChangePoint)
      .catch((err) => {
        // Non-fatal: the price chart and event list still work without it.
        console.warn("Could not load change point results:", err.message);
      });

    fetchEvents()
      .then((body) => {
        const categories = Array.from(new Set(body.data.map((e) => e.category))).sort();
        setAllEventCategories(categories);
      })
      .catch((err) => console.warn("Could not load event categories:", err.message));
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([fetchPrices({ start, end }), fetchEvents({ start, end, category })])
      .then(([priceBody, eventBody]) => {
        if (cancelled) return;
        setPrices(priceBody.data);
        setEvents(eventBody.data);
      })
      .catch((err) => {
        if (cancelled) return;
        const message =
          err instanceof ApiRequestError
            ? err.message
            : "Something went wrong loading dashboard data.";
        setError(message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [start, end, category]);

  const linkedEventIds = useMemo(
    () => new Set((changePoint?.linked_events || []).map((e) => e.event_id)),
    [changePoint]
  );

  const handleReset = () => {
    setStart(DEFAULT_START);
    setEnd(DEFAULT_END);
    setCategory("");
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Brent Oil Price Change Point Dashboard</h1>
        <p>
          Explore how the Bayesian change point model's detected regime shift relates to
          historical Brent oil prices and compiled geopolitical/OPEC/economic events.
        </p>
      </header>

      {changePoint && (
        <section className="change-point-summary">
          <h2>Detected change point</h2>
          <div className="summary-grid">
            <div>
              <span className="summary-label">Date (posterior median)</span>
              <span className="summary-value">{changePoint.change_point_date}</span>
            </div>
            <div>
              <span className="summary-label">95% credible interval</span>
              <span className="summary-value">
                {changePoint.change_point_ci_low} &ndash; {changePoint.change_point_ci_high}
              </span>
            </div>
            <div>
              <span className="summary-label">Volatility change</span>
              <span className="summary-value">
                {changePoint.pct_volatility_change > 0 ? "+" : ""}
                {changePoint.pct_volatility_change?.toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="summary-label">Convergence (max r&#770;)</span>
              <span className="summary-value">
                {changePoint.max_r_hat} {changePoint.converged ? "✓ converged" : "⚠ check diagnostics"}
              </span>
            </div>
          </div>
          <p className="interpretation">{changePoint.interpretation}</p>
        </section>
      )}

      <DateRangeFilter
        start={start}
        end={end}
        category={category}
        categories={allEventCategories}
        onStartChange={setStart}
        onEndChange={setEnd}
        onCategoryChange={setCategory}
        onReset={handleReset}
      />

      {error && <p className="error-banner">{error}</p>}
      {loading && !error && <p className="loading-banner">Loading…</p>}

      <section className="chart-section">
        <PriceChart data={prices} changePoint={changePoint} events={events} />
      </section>

      <section className="events-section">
        <h2>Events in range ({events.length})</h2>
        <EventList events={events} linkedEventIds={linkedEventIds} />
      </section>
    </div>
  );
}
