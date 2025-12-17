import { Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const placeholderData = [
  { name: "Hardware", value: 24 },
  { name: "Software", value: 32 },
  { name: "Access", value: 18 },
  { name: "Network", value: 12 },
  { name: "Other", value: 9 }
];

export function TicketsByCategoryChart() {
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
        <h2 style={{ fontSize: "1.1rem", color: "#1e293b" }}>Tickets by category</h2>
        <p style={{ color: "#64748b", fontSize: "0.95rem" }}>
          Snapshot of open tickets grouped by category.
        </p>
      </header>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={placeholderData}
            dataKey="value"
            nameKey="name"
            fill="#2563eb"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={4}
          />
          <Tooltip
            cursor={{ fill: "rgba(37, 99, 235, 0.08)" }}
            contentStyle={{ borderRadius: "0.75rem", border: "none" }}
          />
        </PieChart>
      </ResponsiveContainer>
    </section>
  );
}
