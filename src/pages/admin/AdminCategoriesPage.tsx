const demoCategories = [
  { name: "Hardware", defaultPriority: "Medium" },
  { name: "Software", defaultPriority: "Medium" },
  { name: "Access", defaultPriority: "High" },
  { name: "Network", defaultPriority: "High" }
];

export function AdminCategoriesPage() {
  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Categories</h1>
        <p style={{ color: "#475569" }}>
          Standardize issue types and routing defaults for consistent triage.
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
              <th style={{ padding: "0.75rem 1rem" }}>Category</th>
              <th style={{ padding: "0.75rem 1rem" }}>Default priority</th>
            </tr>
          </thead>
          <tbody>
            {demoCategories.map((category) => (
              <tr key={category.name} style={{ borderBottom: "1px solid #e2e8f0" }}>
                <td style={{ padding: "0.85rem 1rem" }}>{category.name}</td>
                <td style={{ padding: "0.85rem 1rem" }}>{category.defaultPriority}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
