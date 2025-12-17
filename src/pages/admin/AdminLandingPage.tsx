export function AdminLandingPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Admin overview</h1>
        <p style={{ color: "#475569" }}>
          Manage your service catalog, automation policies, and support teams.
        </p>
      </header>
      <section
        style={{
          display: "grid",
          gap: "1.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))"
        }}
      >
        {["Users & roles", "Teams", "Categories", "SLA policies", "Automation"].map((topic) => (
          <article
            key={topic}
            style={{
              background: "#ffffff",
              padding: "1.5rem",
              borderRadius: "1rem",
              boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
              color: "#475569"
            }}
          >
            <h2 style={{ fontSize: "1.1rem", color: "#1e293b" }}>{topic}</h2>
            <p>Placeholder configuration section for {topic.toLowerCase()}.</p>
          </article>
        ))}
      </section>
    </div>
  );
}
