import type { UserRole } from "../types/auth";
import type { TicketPriority, TicketStatus } from "../types/tickets";

const STATUS_LABELS: Record<TicketStatus, string> = {
  new: "New",
  triaged: "Triaged",
  in_progress: "In Progress",
  waiting_requester: "Waiting on Requester",
  waiting_vendor: "Waiting on Vendor",
  resolved: "Resolved",
  closed: "Closed",
  reopened: "Reopened"
};

const STATUS_COLORS: Record<TicketStatus, string> = {
  new: "#0ea5e9",
  triaged: "#6366f1",
  in_progress: "#2563eb",
  waiting_requester: "#f59e0b",
  waiting_vendor: "#f97316",
  resolved: "#22c55e",
  closed: "#64748b",
  reopened: "#ec4899"
};

const PRIORITY_COLORS: Record<TicketPriority, string> = {
  low: "#38bdf8",
  medium: "#6366f1",
  high: "#f97316",
  critical: "#ef4444"
};

export function getStatusLabel(status: TicketStatus): string {
  return STATUS_LABELS[status];
}

export function getStatusColor(status: TicketStatus): string {
  return STATUS_COLORS[status];
}

export function getPriorityColor(priority: TicketPriority): string {
  return PRIORITY_COLORS[priority];
}

export function getAllowedStatusTransitions(status: TicketStatus, role: UserRole): TicketStatus[] {
  if (role === "admin") {
    return (
      Object.keys(STATUS_LABELS) as TicketStatus[]
    ).filter((candidate) => candidate !== status);
  }

  if (role === "requester") {
    switch (status) {
      case "resolved":
        return ["closed"];
      case "closed":
        return ["reopened"];
      default:
        return [];
    }
  }

  // Agent transitions
  switch (status) {
    case "new":
      return ["triaged", "in_progress"];
    case "triaged":
      return ["in_progress", "waiting_requester"];
    case "in_progress":
      return ["waiting_requester", "waiting_vendor", "resolved"];
    case "waiting_requester":
      return ["in_progress", "resolved"];
    case "waiting_vendor":
      return ["in_progress", "resolved"];
    case "resolved":
      return ["closed", "in_progress"];
    case "reopened":
      return ["triaged", "in_progress"];
    default:
      return [];
  }
}
