import type { UserRole } from "../../types/auth";
import type { TicketStatus } from "../../types/tickets";
import { getAllowedStatusTransitions, getStatusLabel } from "../../lib/ticketHelpers";

interface StatusTransitionMenuProps {
  current: TicketStatus;
  role: UserRole;
  onTransition: (next: TicketStatus) => void;
}

export function StatusTransitionMenu({ current, role, onTransition }: StatusTransitionMenuProps) {
  const options = getAllowedStatusTransitions(current, role);

  if (options.length === 0) {
    return <p style={{ color: "#94a3b8" }}>No transitions available</p>;
  }

  return (
    <div style={{ display: "grid", gap: "0.5rem" }}>
      <span style={{ fontSize: "0.85rem", color: "#64748b" }}>Change status</span>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        {options.map((status) => (
          <button
            type="button"
            key={status}
            onClick={() => onTransition(status)}
            style={{
              padding: "0.45rem 0.8rem",
              borderRadius: "0.75rem",
              border: "1px solid #cbd5f5",
              background: "#ffffff",
              cursor: "pointer",
              fontWeight: 500
            }}
          >
            {getStatusLabel(status)}
          </button>
        ))}
      </div>
    </div>
  );
}
