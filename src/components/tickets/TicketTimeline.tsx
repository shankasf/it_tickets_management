import { formatDistanceToNow } from "date-fns";
import type { AuditEvent, TicketComment } from "../../types/tickets";

interface TicketTimelineProps {
  comments: TicketComment[];
  auditTrail: AuditEvent[];
  activeTab: "conversation" | "internal" | "audit";
}

export function TicketTimeline({ comments, auditTrail, activeTab }: TicketTimelineProps) {
  if (activeTab === "audit") {
    return (
      <ul style={{ display: "grid", gap: "1rem" }}>
        {auditTrail.map((event) => (
          <li
            key={event.id}
            style={{
              background: "#f8fafc",
              padding: "1rem",
              borderRadius: "0.75rem",
              border: "1px solid #e2e8f0"
            }}
          >
            <p style={{ fontWeight: 600, color: "#0f172a" }}>{event.action}</p>
            <p style={{ color: "#475569" }}>By {event.actorId}</p>
            <p style={{ color: "#94a3b8" }}>
              {formatDistanceToNow(new Date(event.createdAt), { addSuffix: true })}
            </p>
          </li>
        ))}
      </ul>
    );
  }

  const filteredComments = comments.filter((comment) =>
    activeTab === "internal" ? comment.isInternal : !comment.isInternal
  );

  if (filteredComments.length === 0) {
    return (
      <div style={{ textAlign: "center", color: "#94a3b8", padding: "2rem" }}>
        No entries yet.
      </div>
    );
  }

  return (
    <ul style={{ display: "grid", gap: "1rem" }}>
      {filteredComments.map((comment) => (
        <li
          key={comment.id}
          style={{
            background: comment.isInternal ? "#fff7ed" : "#ffffff",
            padding: "1rem",
            borderRadius: "0.75rem",
            border: "1px solid #e2e8f0"
          }}
        >
          <p style={{ fontWeight: 600, color: "#0f172a" }}>{comment.authorId}</p>
          <p style={{ color: "#475569" }}>{comment.body}</p>
          <p style={{ color: "#94a3b8" }}>
            {formatDistanceToNow(new Date(comment.createdAt), { addSuffix: true })}
          </p>
        </li>
      ))}
    </ul>
  );
}
