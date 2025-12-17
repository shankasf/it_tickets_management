import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const trendData = [
  { label: "Week 1", created: 54, resolved: 48 },
  { label: "Week 2", created: 62, resolved: 58 },
  { label: "Week 3", created: 71, resolved: 65 },
  { label: "Week 4", created: 66, resolved: 70 }
];

export function TrendsChart() {
  return (
    <section
      style={{
        background: "#ffffff",
        borderRadius: "1rem",
        padding: "1.5rem",
        boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
        display: "grid",
        gap: "1rem"
      }}
    >
      <header>
        <h2 style={{ fontSize: "1.1rem", color: "#1e293b" }}>Ticket volume trend</h2>
        <p style={{ color: "#64748b", fontSize: "0.95rem" }}>
          Weekly snapshot of created versus resolved tickets.
        </p>
      </header>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={trendData}>
          <defs>
            <linearGradient id="areaCreated" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#2563eb" stopOpacity={0.9} />
              <stop offset="95%" stopColor="#2563eb" stopOpacity={0.1} />
            </linearGradient>
            <linearGradient id="areaResolved" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{ borderRadius: "0.75rem", border: "none" }}
            cursor={{ stroke: "#2563eb", strokeWidth: 1 }}
          />
          <Area
            type="monotone"
            dataKey="created"
            stroke="#2563eb"
            fill="url(#areaCreated)"
            strokeWidth={2}
          />
          <Area
            type="monotone"
            dataKey="resolved"
            stroke="#0ea5e9"
            fill="url(#areaResolved)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </section>
  );
}
