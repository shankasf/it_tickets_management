import { ChangeEvent } from "react";
import type { TicketPriority, TicketStatus } from "../../types/tickets";

export interface TicketFiltersState {
  status?: TicketStatus;
  priority?: TicketPriority;
  category?: string;
  assigneeId?: string;
  search?: string;
}

interface TicketFiltersProps {
  value: TicketFiltersState;
  onChange: (next: TicketFiltersState) => void;
}

const statusOptions: Array<{ value: TicketStatus; label: string }> = [
  { value: "new", label: "New" },
  { value: "triaged", label: "Triaged" },
  { value: "in_progress", label: "In Progress" },
  { value: "waiting_requester", label: "Waiting on Requester" },
  { value: "waiting_vendor", label: "Waiting on Vendor" },
  { value: "resolved", label: "Resolved" },
  { value: "closed", label: "Closed" },
  { value: "reopened", label: "Reopened" }
];

const priorityOptions: Array<{ value: TicketPriority; label: string }> = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" }
];

export function TicketFilters({ value, onChange }: TicketFiltersProps) {
  const handleSelect = (
    field: keyof TicketFiltersState,
    event: ChangeEvent<HTMLSelectElement>
  ) => {
    const selected = event.target.value || undefined;
    onChange({ ...value, [field]: selected });
  };

  return (
    <section
      style={{
        display: "grid",
        gap: "1rem",
        background: "#ffffff",
        padding: "1.25rem",
        borderRadius: "1rem",
        boxShadow: "0 12px 32px rgba(15, 23, 42, 0.08)"
      }}
    >
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "1rem"
        }}
      >
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#64748b" }}>
            Status
          </span>
          <select
            value={value.status ?? ""}
            onChange={(event) => handleSelect("status", event)}
            style={{ padding: "0.6rem 0.8rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          >
            <option value="">All</option>
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#64748b" }}>
            Priority
          </span>
          <select
            value={value.priority ?? ""}
            onChange={(event) => handleSelect("priority", event)}
            style={{ padding: "0.6rem 0.8rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          >
            <option value="">All</option>
            {priorityOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#64748b" }}>
            Category
          </span>
          <input
            value={value.category ?? ""}
            onChange={(event) => onChange({ ...value, category: event.target.value || undefined })}
            placeholder="All"
            style={{ padding: "0.6rem 0.8rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
        </label>
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontSize: "0.8rem", textTransform: "uppercase", color: "#64748b" }}>
            Assignee
          </span>
          <input
            value={value.assigneeId ?? ""}
            onChange={(event) =>
              onChange({ ...value, assigneeId: event.target.value || undefined })
            }
            placeholder="All"
            style={{ padding: "0.6rem 0.8rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
        </label>
      </div>
      <input
        placeholder="Search tickets by ID or keyword"
        value={value.search ?? ""}
        onChange={(event) => onChange({ ...value, search: event.target.value || undefined })}
        style={{ padding: "0.7rem 0.9rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
      />
    </section>
  );
}
