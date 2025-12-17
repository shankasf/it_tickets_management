import { useState } from "react";
import { useParams } from "react-router-dom";
import { useAddComment } from "../../hooks/useAddComment";
import { useTicketQuery } from "../../hooks/useTicketQuery";
import { useUpdateTicket } from "../../hooks/useUpdateTicket";
import { useAuth } from "../../app/providers/AuthProvider";
import { CommentComposer } from "../../components/tickets/CommentComposer";
import { TicketMetaPanel } from "../../components/tickets/TicketMetaPanel";
import { TicketTimeline } from "../../components/tickets/TicketTimeline";

export function TicketDetailsPage() {
  const params = useParams<{ ticketId: string }>();
  const ticketId = params.ticketId ?? "";
  const { user } = useAuth();
  const role = user?.role ?? "requester";
  const ticketQuery = useTicketQuery(ticketId);
  const updateTicket = useUpdateTicket({ ticketId });
  const addComment = useAddComment();
  const [activeTab, setActiveTab] = useState<"conversation" | "internal" | "audit">("conversation");

  if (ticketQuery.isLoading) {
    return (
      <div style={{ padding: "2.5rem", textAlign: "center", color: "#64748b" }}>
        Loading ticket...
      </div>
    );
  }

  if (ticketQuery.isError || !ticketQuery.data) {
    return (
      <div style={{ padding: "2.5rem", textAlign: "center", color: "#b91c1c" }}>
        Unable to load ticket. It may have been removed.
      </div>
    );
  }

  const { ticket, comments, auditTrail } = ticketQuery.data;

  const handleAssign = () => {
    if (!user) return;
    updateTicket.mutate({ assigneeId: user.id });
  };

  const handleStatusChange = (status: typeof ticket.status) => {
    updateTicket.mutate({ status });
  };

  const handleComment = ({ body, isInternal }: { body: string; isInternal: boolean }) => {
    addComment.mutate({ ticketId: ticket.id, body, isInternal });
  };

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header style={{ display: "grid", gap: "0.35rem" }}>
        <span style={{ color: "#64748b", fontSize: "0.85rem" }}>Ticket {ticket.id}</span>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>{ticket.title}</h1>
        <p style={{ color: "#475569" }}>{ticket.description}</p>
      </header>
      <div
        style={{
          display: "grid",
          gap: "1.75rem",
          gridTemplateColumns: "minmax(0, 3fr) minmax(0, 1.2fr)"
        }}
      >
        <section style={{ display: "grid", gap: "1.25rem" }}>
          <nav style={{ display: "flex", gap: "1rem" }}>
            <button
              type="button"
              onClick={() => setActiveTab("conversation")}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.75rem",
                border: "none",
                background:
                  activeTab === "conversation"
                    ? "linear-gradient(90deg, #2563eb, #38bdf8)"
                    : "#e2e8f0",
                color: activeTab === "conversation" ? "#ffffff" : "#0f172a",
                fontWeight: 600
              }}
            >
              Conversation
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("internal")}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.75rem",
                border: "none",
                background:
                  activeTab === "internal" ? "linear-gradient(90deg, #2563eb, #38bdf8)" : "#e2e8f0",
                color: activeTab === "internal" ? "#ffffff" : "#0f172a",
                fontWeight: 600
              }}
            >
              Internal notes
            </button>
            <button
              type="button"
              onClick={() => setActiveTab("audit")}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "0.75rem",
                border: "none",
                background:
                  activeTab === "audit" ? "linear-gradient(90deg, #2563eb, #38bdf8)" : "#e2e8f0",
                color: activeTab === "audit" ? "#ffffff" : "#0f172a",
                fontWeight: 600
              }}
            >
              Audit log
            </button>
          </nav>
          <TicketTimeline comments={comments} auditTrail={auditTrail} activeTab={activeTab} />
          <CommentComposer
            onSubmit={handleComment}
            disabled={addComment.isPending}
            allowInternal={role !== "requester"}
          />
        </section>
        <TicketMetaPanel
          ticket={ticket}
          role={role}
          isUpdating={updateTicket.isPending}
          onAssignToSelf={handleAssign}
          onStatusChange={handleStatusChange}
        />
      </div>
    </div>
  );
}
