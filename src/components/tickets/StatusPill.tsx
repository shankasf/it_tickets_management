import type { TicketStatus } from "../../types/tickets";
import { getStatusColor, getStatusLabel } from "../../lib/ticketHelpers";

export function StatusPill({ status }: { status: TicketStatus }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0.25rem 0.65rem",
        borderRadius: "999px",
        fontSize: "0.75rem",
        fontWeight: 600,
        background: `${getStatusColor(status)}1a`,
        color: getStatusColor(status)
      }}
    >
      {getStatusLabel(status)}
    </span>
  );
}
