import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div
      style={{
        display: "grid",
        placeItems: "center",
        minHeight: "60vh",
        textAlign: "center",
        gap: "1rem"
      }}
    >
      <h1 style={{ fontSize: "3rem", color: "#0f172a" }}>404</h1>
      <p style={{ color: "#475569" }}>The page you are looking for could not be found.</p>
      <Link
        to="/dashboard"
        style={{
          padding: "0.75rem 1.25rem",
          borderRadius: "0.85rem",
          background: "linear-gradient(90deg, #2563eb, #38bdf8)",
          color: "#ffffff",
          fontWeight: 600
        }}
      >
        Back to dashboard
      </Link>
    </div>
  );
}
