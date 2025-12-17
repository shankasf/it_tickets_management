import { useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import { useAuth } from "../app/providers/AuthProvider";

interface AddCommentInput {
  ticketId: string;
  body: string;
  isInternal?: boolean;
}

export function useAddComment() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation({
    mutationFn: ({ ticketId, body, isInternal }: AddCommentInput) => {
      if (!user) {
        throw new Error("Must be authenticated to comment on a ticket");
      }
      return api.addComment(ticketId, {
        body,
        isInternal,
        authorId: user.id
      });
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["tickets", variables.ticketId] });
    }
  });
}
