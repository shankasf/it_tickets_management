import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { Ticket } from "../types/tickets";
import { useAuth } from "../app/providers/AuthProvider";

interface UseUpdateTicketProps {
  ticketId: string;
}

export function useUpdateTicket({ ticketId }: UseUpdateTicketProps) {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: (patch: Partial<Ticket>) => {
      if (!user) {
        throw new Error("Must be authenticated to update a ticket");
      }
      return api.updateTicket(ticketId, patch, user);
    },
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      queryClient.invalidateQueries({ queryKey: ["tickets", ticketId] });
      queryClient.setQueryData(["tickets", ticketId], (current: unknown) => {
        if (!current || typeof current !== "object") return current;
        const snapshot = current as { ticket: Ticket };
        return { ...snapshot, ticket: updated };
      });
    }
  });
}
