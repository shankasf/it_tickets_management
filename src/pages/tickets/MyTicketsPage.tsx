import { useMemo } from "react";
import { useTicketsQuery } from "../../hooks/useTicketsQuery";
import { useAuth } from "../../app/providers/AuthProvider";
import { TicketTable } from "../../components/tickets/TicketTable";

export function MyTicketsPage() {
  const { user } = useAuth();
  const requesterId = user?.id;
  const ticketsQuery = useTicketsQuery({ requesterId });

  const heading = useMemo(() => {
    if (!user) return "My tickets";
    return `Tickets created by ${user.name}`;
  }, [user]);

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>{heading}</h1>
        <p style={{ color: "#475569" }}>
          Track progress on tickets you have opened and respond to agent updates.
        </p>
      </header>
      {ticketsQuery.isLoading ? (
        <div
          style={{
            background: "#ffffff",
            borderRadius: "1rem",
            padding: "2.5rem",
            textAlign: "center",
            color: "#64748b"
          }}
        >
          Loading your tickets...
        </div>
      ) : (
        <TicketTable
          tickets={ticketsQuery.data ?? []}
          selectedIds={[]}
          onSelectionChange={() => undefined}
        />
      )}
    </div>
  );
}
