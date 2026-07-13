// Date-range picker plus event-category filter for the dashboard, so a
// stakeholder can narrow the price chart and event list to a period of
// interest (e.g., "show me around the 2008 change point").
export default function DateRangeFilter({
  start,
  end,
  category,
  categories,
  onStartChange,
  onEndChange,
  onCategoryChange,
  onReset,
}) {
  return (
    <div className="filter-bar">
      <label>
        From
        <input type="date" value={start} onChange={(e) => onStartChange(e.target.value)} />
      </label>
      <label>
        To
        <input type="date" value={end} onChange={(e) => onEndChange(e.target.value)} />
      </label>
      <label>
        Event category
        <select value={category} onChange={(e) => onCategoryChange(e.target.value)}>
          <option value="">All</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </label>
      <button type="button" onClick={onReset}>
        Reset
      </button>
    </div>
  );
}
