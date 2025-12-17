const demoTeams = [
  { name: "Core Support", members: 8, focus: "L1 triage" },
  { name: "Infrastructure", members: 5, focus: "Network & servers" },
  { name: "Business Apps", members: 6, focus: "SaaS & ERP" }
];

export function AdminTeamsPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Teams</h1>
        <p style={{ color: "#475569" }}>
          Organize agents into teams to simplify routing and escalation.
        </p>
      </header>
      <section
        style={{
          display: "grid",
          gap: "1rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))"
        }}
      >
        {demoTeams.map((team) => (
          <article
            key={team.name}
            style={{
              background: "#ffffff",
              padding: "1.5rem",
              borderRadius: "1rem",
              boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
              display: "grid",
              gap: "0.5rem"
            }}
          >
            <h2 style={{ fontSize: "1.1rem", color: "#1e293b" }}>{team.name}</h2>
            <p style={{ color: "#64748b" }}>{team.focus}</p>
            <p style={{ color: "#475569" }}>Members: {team.members}</p>
          </article>
        ))}
      </section>
    </div>
  );
}
