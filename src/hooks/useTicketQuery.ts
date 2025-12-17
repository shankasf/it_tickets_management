import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useTicketQuery(ticketId: string) {
  return useQuery({
    queryKey: ["tickets", ticketId],
    queryFn: () => api.getTicket(ticketId),
    enabled: Boolean(ticketId)
  });
}
