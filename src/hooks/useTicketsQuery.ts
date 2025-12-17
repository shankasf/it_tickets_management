import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Ticket } from "../types/tickets";

export interface TicketsQueryVariables {
  status?: Ticket["status"];
  priority?: Ticket["priority"];
  category?: Ticket["category"];
  assigneeId?: string;
  requesterId?: string;
  search?: string;
}

export function useTicketsQuery(variables: TicketsQueryVariables) {
  return useQuery({
    queryKey: ["tickets", variables],
    queryFn: () => api.getTickets(variables),
    staleTime: 30_000
  });
}
