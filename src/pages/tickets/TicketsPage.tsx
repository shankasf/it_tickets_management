import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTicketsQuery } from "../../hooks/useTicketsQuery";
import { TicketFilters, TicketFiltersState } from "../../components/tickets/TicketFilters";
import { TicketTable } from "../../components/tickets/TicketTable";
import type { Ticket } from "../../types/tickets";

export function TicketsPage() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<TicketFiltersState>({});
  const [selected, setSelected] = useState<string[]>([]);
  const ticketsQuery = useTicketsQuery(filters);

  const hasSelection = selected.length > 0;
  const bulkSummary = useMemo(() => {
    if (!hasSelection) {
      return "Select tickets to perform actions";
    }
    return `${selected.length} ticket${selected.length > 1 ? "s" : ""} selected`;
  }, [hasSelection, selected.length]);

  const handleRowClick = (ticket: Ticket) => {
    navigate(`/tickets/${ticket.id}`);
  };

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Tickets</h1>
          <p style={{ color: "#475569" }}>Monitor and triage tickets across teams and priorities.</p>
        </div>
        <button
          type="button"
          onClick={() => navigate("/tickets/new")}
          style={{
            padding: "0.75rem 1.2rem",
            borderRadius: "0.85rem",
            border: "none",
            background: "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            cursor: "pointer"
          }}
        >
          Create ticket
        </button>
      </header>
      <TicketFilters value={filters} onChange={setFilters} />
      <section
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "#ffffff",
          padding: "0.9rem 1.25rem",
          borderRadius: "1rem",
          boxShadow: "0 8px 18px rgba(15, 23, 42, 0.08)"
        }}
      >
        <span style={{ color: "#475569" }}>{bulkSummary}</span>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button
            type="button"
            disabled={!hasSelection}
            style={{
              padding: "0.55rem 1rem",
              borderRadius: "0.75rem",
              border: "1px solid #cbd5f5",
              background: hasSelection ? "#ffffff" : "#f8fafc",
              color: hasSelection ? "#1d4ed8" : "#94a3b8",
              cursor: hasSelection ? "pointer" : "not-allowed"
            }}
          >
            Assign
          </button>
          <button
            type="button"
            disabled={!hasSelection}
            style={{
              padding: "0.55rem 1rem",
              borderRadius: "0.75rem",
              border: "1px solid #cbd5f5",
              background: hasSelection ? "#ffffff" : "#f8fafc",
              color: hasSelection ? "#1d4ed8" : "#94a3b8",
              cursor: hasSelection ? "pointer" : "not-allowed"
            }}
          >
            Change status
          </button>
        </div>
      </section>
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
          Loading tickets...
        </div>
      ) : (
        <TicketTable
          tickets={ticketsQuery.data ?? []}
          selectedIds={selected}
          onSelectionChange={setSelected}
          onRowClick={handleRowClick}
        />
      )}
    </div>
  );
}
