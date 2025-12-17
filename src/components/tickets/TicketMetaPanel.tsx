import type { UserRole } from "../../types/auth";
import type { Ticket } from "../../types/tickets";
import { PriorityBadge } from "./PriorityBadge";
import { StatusPill } from "./StatusPill";
import { StatusTransitionMenu } from "./StatusTransitionMenu";

interface TicketMetaPanelProps {
  ticket: Ticket;
  role: UserRole;
  isUpdating: boolean;
  onAssignToSelf: () => void;
  onStatusChange: (status: Ticket["status"]) => void;
}

export function TicketMetaPanel({ ticket, role, isUpdating, onAssignToSelf, onStatusChange }: TicketMetaPanelProps) {
  const canAssign = role === "agent" || role === "admin";

  return (
    <aside
      style={{
        display: "grid",
        gap: "1.5rem",
        background: "#f8fafc",
        padding: "1.5rem",
        borderRadius: "1rem",
        alignSelf: "flex-start"
      }}
    >
      <section style={{ display: "grid", gap: "0.75rem" }}>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <StatusPill status={ticket.status} />
          <PriorityBadge priority={ticket.priority} />
        </div>
        <div style={{ fontSize: "0.95rem", color: "#475569" }}>
          <strong>Category:</strong> {ticket.category}
        </div>
        <div style={{ fontSize: "0.95rem", color: "#475569" }}>
          <strong>Requester:</strong> {ticket.requesterId}
        </div>
        <div style={{ fontSize: "0.95rem", color: "#475569" }}>
          <strong>Assignee:</strong> {ticket.assigneeId ?? "Unassigned"}
        </div>
      </section>
      {canAssign ? (
        <button
          type="button"
          onClick={onAssignToSelf}
          disabled={isUpdating}
          style={{
            padding: "0.75rem 1rem",
            borderRadius: "0.85rem",
            border: "none",
            background: "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            cursor: isUpdating ? "not-allowed" : "pointer"
          }}
        >
          Assign to me
        </button>
      ) : null}
      <StatusTransitionMenu current={ticket.status} role={role} onTransition={onStatusChange} />
    </aside>
  );
}
