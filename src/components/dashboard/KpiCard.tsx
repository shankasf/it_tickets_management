interface KpiCardProps {
  title: string;
  value: string;
  description?: string;
}

export function KpiCard({ title, value, description }: KpiCardProps) {
  return (
    <article
      style={{
        background: "#ffffff",
        borderRadius: "1rem",
        padding: "1.5rem",
        boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)",
        display: "grid",
        gap: "0.5rem"
      }}
    >
      <span style={{ fontSize: "0.9rem", color: "#64748b", textTransform: "uppercase" }}>
        {title}
      </span>
      <strong style={{ fontSize: "2rem", color: "#1e293b" }}>{value}</strong>
      {description ? <p style={{ color: "#475569" }}>{description}</p> : null}
    </article>
  );
}
