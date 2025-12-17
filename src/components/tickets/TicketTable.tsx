import { ChangeEvent } from "react";
import { formatDistanceToNow } from "date-fns";
import type { Ticket } from "../../types/tickets";
import { PriorityBadge } from "./PriorityBadge";
import { StatusPill } from "./StatusPill";

interface TicketTableProps {
  tickets: Ticket[];
  selectedIds: string[];
  onSelectionChange: (next: string[]) => void;
  onRowClick?: (ticket: Ticket) => void;
}

export function TicketTable({ tickets, selectedIds, onSelectionChange, onRowClick }: TicketTableProps) {
  const allSelected = tickets.length > 0 && selectedIds.length === tickets.length;

  const toggleAll = (event: ChangeEvent<HTMLInputElement>) => {
    onSelectionChange(event.target.checked ? tickets.map((ticket) => ticket.id) : []);
  };

  const toggleRow = (event: ChangeEvent<HTMLInputElement>, ticketId: string) => {
    const next = event.target.checked
      ? [...selectedIds, ticketId]
      : selectedIds.filter((id) => id !== ticketId);
    onSelectionChange(next);
  };

  return (
    <div
      style={{
        overflow: "hidden",
        borderRadius: "1rem",
        background: "#ffffff",
        boxShadow: "0 18px 38px rgba(15, 23, 42, 0.08)"
      }}
    >
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead style={{ textAlign: "left", background: "#f8fafc", color: "#475569" }}>
          <tr>
            <th style={{ padding: "0.75rem 1rem", width: "3rem" }}>
              <input type="checkbox" checked={allSelected} onChange={toggleAll} aria-label="Select all tickets" />
            </th>
            <th style={{ padding: "0.75rem 1rem" }}>Ticket</th>
            <th style={{ padding: "0.75rem 1rem" }}>Status</th>
            <th style={{ padding: "0.75rem 1rem" }}>Priority</th>
            <th style={{ padding: "0.75rem 1rem" }}>Category</th>
            <th style={{ padding: "0.75rem 1rem" }}>Assignee</th>
            <th style={{ padding: "0.75rem 1rem", textAlign: "right" }}>Updated</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => {
            const selected = selectedIds.includes(ticket.id);
            return (
              <tr
                key={ticket.id}
                style={{
                  borderBottom: "1px solid #e2e8f0",
                  cursor: onRowClick ? "pointer" : "default",
                  background: selected ? "#edf2ff" : "inherit"
                }}
                onClick={() => onRowClick?.(ticket)}
              >
                <td style={{ padding: "0.75rem 1rem" }} onClick={(event) => event.stopPropagation()}>
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(event) => toggleRow(event, ticket.id)}
                    aria-label={`Select ticket ${ticket.id}`}
                  />
                </td>
                <td style={{ padding: "0.75rem 1rem" }}>
                  <div style={{ display: "grid", gap: "0.2rem" }}>
                    <strong>{ticket.title}</strong>
                    <span style={{ color: "#64748b", fontSize: "0.85rem" }}>{ticket.id}</span>
                  </div>
                </td>
                <td style={{ padding: "0.75rem 1rem" }}>
                  <StatusPill status={ticket.status} />
                </td>
                <td style={{ padding: "0.75rem 1rem" }}>
                  <PriorityBadge priority={ticket.priority} />
                </td>
                <td style={{ padding: "0.75rem 1rem", color: "#334155" }}>{ticket.category}</td>
                <td style={{ padding: "0.75rem 1rem", color: "#334155" }}>
                  {ticket.assigneeId ? ticket.assigneeId : "Unassigned"}
                </td>
                <td style={{ padding: "0.75rem 1rem", textAlign: "right", color: "#475569" }}>
                  {formatDistanceToNow(new Date(ticket.updatedAt), { addSuffix: true })}
                </td>
              </tr>
            );
          })}
          {tickets.length === 0 ? (
            <tr>
              <td colSpan={7} style={{ padding: "2rem", textAlign: "center", color: "#64748b" }}>
                No tickets found. Adjust filters or create a new ticket.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
