// Scrollable list of events in the currently filtered range, with the
// detected change point's linked events (from Task 2) highlighted first.
export default function EventList({ events, linkedEventIds }) {
  if (!events || events.length === 0) {
    return <p className="empty-state">No events in the selected range/category.</p>;
  }

  return (
    <ul className="event-list">
      {events.map((event) => {
        const isLinked = linkedEventIds.has(event.event_id);
        return (
          <li key={event.event_id} className={isLinked ? "event-item linked" : "event-item"}>
            <div className="event-item-header">
              <span className="event-date">{event.date}</span>
              <span className="event-category">{event.category}</span>
              {isLinked && <span className="event-badge">Near change point</span>}
            </div>
            <div className="event-name">{event.event_name}</div>
            <p className="event-description">{event.description}</p>
          </li>
        );
      })}
    </ul>
  );
}
