export function ReportsPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Reports & analytics</h1>
        <p style={{ color: "#475569" }}>
          Analyze ticket volumes, SLA adherence, and team performance over time.
        </p>
      </header>
      <section
        style={{
          background: "#ffffff",
          padding: "2rem",
          borderRadius: "1rem",
          boxShadow: "0 20px 48px rgba(15, 23, 42, 0.08)",
          display: "grid",
          gap: "1.25rem"
        }}
      >
        <h2 style={{ fontSize: "1.25rem", color: "#1e293b" }}>Filters</h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: "1rem"
          }}
        >
          <input
            placeholder="Date range"
            style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
          <input
            placeholder="Team"
            style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
          <input
            placeholder="Category"
            style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
        </div>
        <button
          type="button"
          style={{
            padding: "0.75rem 1.25rem",
            borderRadius: "0.85rem",
            border: "none",
            background: "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            justifySelf: "start"
          }}
        >
          Export CSV
        </button>
      </section>
      <section
        style={{
          display: "grid",
          gap: "1.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))"
        }}
      >
        {["SLA compliance", "Mean time to resolve", "Ticket volume", "Top requesters"].map((title) => (
          <article
            key={title}
            style={{
              background: "#ffffff",
              padding: "1.5rem",
              borderRadius: "1rem",
              boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
              color: "#475569"
            }}
          >
            <h3 style={{ fontSize: "1.1rem", color: "#1e293b", marginBottom: "0.5rem" }}>{title}</h3>
            <p>Placeholder data pending integration with analytics service.</p>
          </article>
        ))}
      </section>
    </div>
  );
}
