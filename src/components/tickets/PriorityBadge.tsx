import type { TicketPriority } from "../../types/tickets";
import { getPriorityColor } from "../../lib/ticketHelpers";

export function PriorityBadge({ priority }: { priority: TicketPriority }) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "0.3rem",
        borderRadius: "0.5rem",
        padding: "0.2rem 0.6rem",
        fontSize: "0.75rem",
        fontWeight: 600,
        color: getPriorityColor(priority),
        background: `${getPriorityColor(priority)}14`
      }}
    >
      <span
        aria-hidden
        style={{
          width: "0.4rem",
          height: "0.4rem",
          borderRadius: "999px",
          background: getPriorityColor(priority)
        }}
      />
      {priority.toUpperCase()}
    </span>
  );
}
