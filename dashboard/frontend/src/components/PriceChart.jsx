import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ReferenceArea,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

// Renders the historical Brent price series with:
// - a shaded band for the change point's 95% credible interval
// - a vertical marker line at the posterior median change point date
// - vertical event markers (as a light ReferenceLine per visible event)
export default function PriceChart({ data, changePoint, events }) {
  if (!data || data.length === 0) {
    return <p className="empty-state">No price data in the selected range.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={420}>
      <AreaChart data={data} margin={{ top: 10, right: 24, left: 8, bottom: 8 }}>
        <defs>
          <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1f4e79" stopOpacity={0.35} />
            <stop offset="95%" stopColor="#1f4e79" stopOpacity={0.02} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
        <XAxis dataKey="date" minTickGap={60} />
        <YAxis
          label={{ value: "USD / barrel", angle: -90, position: "insideLeft" }}
          domain={["auto", "auto"]}
        />
        <Tooltip
          formatter={(value, name) => [value, name === "price" ? "Price (USD)" : name]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Legend />
        <Area
          type="monotone"
          dataKey="price"
          name="Brent price"
          stroke="#1f4e79"
          fill="url(#priceFill)"
          isAnimationActive={false}
          connectNulls
        />

        {changePoint?.change_point_ci_low && changePoint?.change_point_ci_high && (
          <ReferenceArea
            x1={changePoint.change_point_ci_low}
            x2={changePoint.change_point_ci_high}
            fill="#d9822b"
            fillOpacity={0.15}
            label={{ value: "95% CI", position: "insideTopLeft", fill: "#d9822b", fontSize: 11 }}
          />
        )}
        {changePoint?.change_point_date && (
          <ReferenceLine
            x={changePoint.change_point_date}
            stroke="#d9822b"
            strokeWidth={2}
            label={{ value: "Change point", position: "top", fill: "#d9822b", fontSize: 11 }}
          />
        )}

        {events.map((event) => (
          <ReferenceLine
            key={event.event_id}
            x={event.date}
            stroke="#7a7a7a"
            strokeDasharray="4 2"
            opacity={0.6}
          />
        ))}
      </AreaChart>
    </ResponsiveContainer>
  );
}
