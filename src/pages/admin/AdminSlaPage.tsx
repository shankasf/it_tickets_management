const slaPolicies = [
  { priority: "Critical", response: "15 minutes", resolve: "4 hours" },
  { priority: "High", response: "1 hour", resolve: "8 hours" },
  { priority: "Medium", response: "4 hours", resolve: "24 hours" },
  { priority: "Low", response: "1 business day", resolve: "3 business days" }
];

export function AdminSlaPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>SLA policies</h1>
        <p style={{ color: "#475569" }}>
          Define response and resolution targets by priority to measure performance.
        </p>
      </header>
      <section
        style={{
          background: "#ffffff",
          padding: "2rem",
          borderRadius: "1rem",
          boxShadow: "0 20px 48px rgba(15, 23, 42, 0.08)"
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead style={{ textAlign: "left", background: "#f8fafc", color: "#475569" }}>
            <tr>
              <th style={{ padding: "0.75rem 1rem" }}>Priority</th>
              <th style={{ padding: "0.75rem 1rem" }}>First response target</th>
              <th style={{ padding: "0.75rem 1rem" }}>Resolution target</th>
            </tr>
          </thead>
          <tbody>
            {slaPolicies.map((policy) => (
              <tr key={policy.priority} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.85rem 1rem" }}>{policy.priority}</td>
                <td style={{ padding: "0.85rem 1rem" }}>{policy.response}</td>
                <td style={{ padding: "0.85rem 1rem" }}>{policy.resolve}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
