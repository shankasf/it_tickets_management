import { v4 as uuid } from "uuid";
import type {
  AuditEvent,
  Ticket,
  TicketAttachment,
  TicketComment,
  TicketPriority,
  TicketStatus
} from "../types/tickets";
import type { AuthUser } from "../types/auth";

interface TicketFilters {
  status?: TicketStatus;
  priority?: TicketPriority;
  category?: string;
  assigneeId?: string;
  requesterId?: string;
  search?: string;
}

interface CreateTicketPayload {
  title: string;
  description: string;
  category: string;
  priority: TicketPriority;
  requesterId: string;
  attachments?: TicketAttachment[];
}

interface UpdateTicketPayload {
  status?: TicketStatus;
  assigneeId?: string;
  priority?: TicketPriority;
  category?: string;
  title?: string;
  description?: string;
}

interface AddCommentPayload {
  body: string;
  isInternal?: boolean;
  authorId: string;
}

// Simple in-memory dataset for the prototype.
const tickets: Ticket[] = [
  {
    id: "TCK-1001",
    title: "Laptop screen flickering",
    description: "Display intermittently flickers; especially on battery power.",
    status: "in_progress",
    priority: "high",
    category: "Hardware",
    requesterId: "demo-requester",
    assigneeId: "demo-agent",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
    updatedAt: new Date().toISOString(),
    slaPolicyId: "sla-standard"
  },
  {
    id: "TCK-1002",
    title: "VPN unable to connect",
    description: "VPN client fails with error 721 when connecting from home.",
    status: "triaged",
    priority: "medium",
    category: "Network",
    requesterId: "demo-requester",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 50).toISOString()
  }
];

const comments: TicketComment[] = [
  {
    id: "TCOM-1",
    ticketId: "TCK-1001",
    authorId: "demo-agent",
    body: "Investigating GPU driver updates as the likely fix.",
    isInternal: false,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString()
  }
];

const auditEvents: AuditEvent[] = [
  {
    id: "TAUD-1",
    ticketId: "TCK-1001",
    action: "status_changed",
    actorId: "demo-agent",
    meta: { from: "triaged", to: "in_progress" },
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2.5).toISOString()
  }
];

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const api = {
  async getTickets(filters: TicketFilters = {}): Promise<Ticket[]> {
    await delay(180);
    return tickets.filter((ticket) => {
      if (filters.status && ticket.status !== filters.status) return false;
      if (filters.priority && ticket.priority !== filters.priority) return false;
      if (filters.category && ticket.category !== filters.category) return false;
      if (filters.assigneeId && ticket.assigneeId !== filters.assigneeId) return false;
      if (filters.requesterId && ticket.requesterId !== filters.requesterId) return false;
      if (filters.search) {
        const query = filters.search.toLowerCase();
        const inTitle = ticket.title.toLowerCase().includes(query);
        const inDescription = ticket.description.toLowerCase().includes(query);
        if (!inTitle && !inDescription) return false;
      }
      return true;
    });
  },

  async getTicket(id: string): Promise<{
    ticket: Ticket;
    comments: TicketComment[];
    auditTrail: AuditEvent[];
  }> {
    await delay(160);
    const ticket = tickets.find((item) => item.id === id);
    if (!ticket) {
      throw new Error("Ticket not found");
    }
    return {
      ticket,
      comments: comments.filter((comment) => comment.ticketId === id),
      auditTrail: auditEvents.filter((event) => event.ticketId === id)
    };
  },

  async createTicket(payload: CreateTicketPayload): Promise<Ticket> {
    await delay(200);
    const newTicket: Ticket = {
      id: `TCK-${Math.floor(Math.random() * 9000) + 1000}`,
      status: "new",
      priority: payload.priority,
      title: payload.title,
      description: payload.description,
      category: payload.category,
      requesterId: payload.requesterId,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };
    tickets.push(newTicket);
    auditEvents.push({
      id: uuid(),
      ticketId: newTicket.id,
      action: "ticket_created",
      actorId: payload.requesterId,
      meta: {},
      createdAt: newTicket.createdAt
    });
    return newTicket;
  },

  async updateTicket(id: string, patch: UpdateTicketPayload, actor: AuthUser): Promise<Ticket> {
    await delay(200);
    const ticketIndex = tickets.findIndex((ticket) => ticket.id === id);
    if (ticketIndex === -1) {
      throw new Error("Ticket not found");
    }
    const existing = tickets[ticketIndex];
    const updated: Ticket = {
      ...existing,
      ...patch,
      updatedAt: new Date().toISOString()
    };
    tickets[ticketIndex] = updated;
    const metaPayload = Object.entries(patch).reduce<Record<string, unknown>>(
      (accumulator, [key, value]) => {
        if (value !== undefined) {
          accumulator[key] = value as unknown;
        }
        return accumulator;
      },
      {}
    );
    auditEvents.push({
      id: uuid(),
      ticketId: id,
      action: "ticket_updated",
      actorId: actor.id,
      meta: metaPayload,
      createdAt: updated.updatedAt
    });
    return updated;
  },

  async addComment(ticketId: string, payload: AddCommentPayload): Promise<TicketComment> {
    await delay(160);
    const comment: TicketComment = {
      id: uuid(),
      ticketId,
      body: payload.body,
      isInternal: Boolean(payload.isInternal),
      authorId: payload.authorId,
      createdAt: new Date().toISOString()
    };
    comments.push(comment);
    auditEvents.push({
      id: uuid(),
      ticketId,
      action: payload.isInternal ? "internal_note_added" : "comment_added",
      actorId: payload.authorId,
      meta: {},
      createdAt: comment.createdAt
    });
    return comment;
  },

  async uploadAttachment(ticketId: string, file: File): Promise<TicketAttachment> {
    await delay(240);
    return {
      id: uuid(),
      ticketId,
      filename: file.name,
      url: URL.createObjectURL(file),
      size: file.size
    };
  }
};
