export type TicketStatus =
  | "new"
  | "triaged"
  | "in_progress"
  | "waiting_requester"
  | "waiting_vendor"
  | "resolved"
  | "closed"
  | "reopened";

export type TicketPriority = "low" | "medium" | "high" | "critical";

export interface Ticket {
  id: string;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  category: string;
  requesterId: string;
  assigneeId?: string;
  createdAt: string;
  updatedAt: string;
  dueAt?: string;
  slaPolicyId?: string;
}

export interface TicketComment {
  id: string;
  ticketId: string;
  authorId: string;
  body: string;
  isInternal: boolean;
  createdAt: string;
}

export interface TicketAttachment {
  id: string;
  ticketId: string;
  filename: string;
  url: string;
  size: number;
}

export interface AuditEvent {
  id: string;
  ticketId: string;
  action: string;
  actorId: string;
  meta: Record<string, unknown>;
  createdAt: string;
}
