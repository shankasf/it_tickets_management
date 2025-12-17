import { FormEvent, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../../app/providers/AuthProvider";
import type { UserRole } from "../../types/auth";

export function LoginPage() {
  const { user, loginAs } = useAuth();
  const location = useLocation();
  const [role, setRole] = useState<UserRole>("agent");

  const from = (location.state as { from?: Location })?.from?.pathname ?? "/dashboard";

  if (user) {
    return <Navigate to={from} replace />;
  }

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    loginAs(role);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        background: "linear-gradient(135deg, #1d4ed8, #2563eb)"
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#ffffff",
          padding: "2.5rem",
          borderRadius: "1rem",
          boxShadow: "0 20px 60px rgba(15, 23, 42, 0.18)",
          width: "min(420px, 90vw)",
          display: "grid",
          gap: "1.5rem"
        }}
      >
        <header style={{ display: "grid", gap: "0.5rem" }}>
          <h1 style={{ fontSize: "1.75rem" }}>IT Service Desk</h1>
          <p style={{ color: "#475569" }}>Use the quick start roles to explore the dashboard.</p>
        </header>
        <label style={{ display: "grid", gap: "0.75rem" }}>
          <span style={{ fontWeight: 600 }}>Sign in as</span>
          <select
            value={role}
            onChange={(event) => setRole(event.target.value as UserRole)}
            style={{
              padding: "0.85rem 1rem",
              borderRadius: "0.75rem",
              border: "1px solid #cbd5f5",
              fontSize: "1rem"
            }}
          >
            <option value="requester">Requester</option>
            <option value="agent">Agent</option>
            <option value="admin">Admin</option>
          </select>
        </label>
        <button
          type="submit"
          style={{
            padding: "0.9rem 1rem",
            borderRadius: "0.75rem",
            border: "none",
            background: "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            fontSize: "1rem",
            cursor: "pointer"
          }}
        >
          Continue
        </button>
      </form>
    </div>
  );
}
