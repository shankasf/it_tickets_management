const demoUsers = [
  { id: "demo-requester", name: "Riley Requester", role: "Requester", team: "Employees" },
  { id: "demo-agent", name: "Avery Agent", role: "Agent", team: "Core Support" },
  { id: "demo-admin", name: "Alex Admin", role: "Admin", team: "IT Leadership" }
];

export function AdminUsersPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Users & roles</h1>
        <p style={{ color: "#475569" }}>
          Invite agents, assign roles, and manage access in your organization.
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
              <th style={{ padding: "0.75rem 1rem" }}>Name</th>
              <th style={{ padding: "0.75rem 1rem" }}>Role</th>
              <th style={{ padding: "0.75rem 1rem" }}>Team</th>
            </tr>
          </thead>
          <tbody>
            {demoUsers.map((user) => (
              <tr key={user.id} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.85rem 1rem" }}>{user.name}</td>
                <td style={{ padding: "0.85rem 1rem" }}>{user.role}</td>
                <td style={{ padding: "0.85rem 1rem" }}>{user.team}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
