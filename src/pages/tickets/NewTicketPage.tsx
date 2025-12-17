import { useMutation, useQueryClient } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";
import { api } from "../../api/client";
import { useAuth } from "../../app/providers/AuthProvider";
import type { TicketPriority } from "../../types/tickets";

const priorities: Array<{ value: TicketPriority; label: string }> = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" }
];

const formSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  category: z.string().min(1, "Please choose a category"),
  location: z.string().optional(),
  priority: z.enum(["low", "medium", "high", "critical"] as const),
  description: z.string().min(10, "Provide enough detail for agents to triage")
});

type FormValues = z.infer<typeof formSchema>;

export function NewTicketPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      category: "Hardware",
      location: "",
      priority: "medium",
      description: ""
    }
  });

  const createTicket = useMutation({
    mutationFn: (payload: FormValues) => {
      if (!user) {
        throw new Error("You must be signed in to create a ticket");
      }
      return api.createTicket({
        title: payload.title,
        description: payload.description,
        category: payload.category,
        priority: payload.priority,
        requesterId: user.id
      });
    },
    onSuccess: (ticket) => {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
      navigate(`/tickets/${ticket.id}`, { replace: true, state: { fromCreate: true } });
    }
  });

  return (
    <div style={{ display: "grid", gap: "1.5rem" }}>
      <header style={{ display: "grid", gap: "0.5rem" }}>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Create ticket</h1>
        <p style={{ color: "#475569" }}>
          Provide enough detail for the support team to triage and resolve quickly.
        </p>
      </header>
      <form
        onSubmit={form.handleSubmit((values) => createTicket.mutate(values))}
        style={{
          display: "grid",
          gap: "1.5rem",
          background: "#ffffff",
          padding: "2rem",
          borderRadius: "1rem",
          boxShadow: "0 20px 48px rgba(15, 23, 42, 0.08)"
        }}
      >
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontWeight: 600 }}>Title</span>
          <input
            {...form.register("title")}
            placeholder="Summarize the issue"
            style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
          />
          {form.formState.errors.title ? (
            <span style={{ color: "#ef4444" }}>{form.formState.errors.title.message}</span>
          ) : null}
        </label>
        <div
          style={{
            display: "grid",
            gap: "1rem",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))"
          }}
        >
          <label style={{ display: "grid", gap: "0.5rem" }}>
            <span style={{ fontWeight: 600 }}>Category</span>
            <input
              {...form.register("category")}
              placeholder="Hardware, Software, Access..."
              style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
            />
            {form.formState.errors.category ? (
              <span style={{ color: "#ef4444" }}>{form.formState.errors.category.message}</span>
            ) : null}
          </label>
          <label style={{ display: "grid", gap: "0.5rem" }}>
            <span style={{ fontWeight: 600 }}>Location or asset</span>
            <input
              {...form.register("location")}
              placeholder="Building, floor, asset tag"
              style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
            />
          </label>
          <label style={{ display: "grid", gap: "0.5rem" }}>
            <span style={{ fontWeight: 600 }}>Priority</span>
            <select
              {...form.register("priority")}
              style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5" }}
            >
              {priorities.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label style={{ display: "grid", gap: "0.5rem" }}>
          <span style={{ fontWeight: 600 }}>Description</span>
          <textarea
            {...form.register("description")}
            rows={6}
            placeholder="Describe the issue, steps taken, and any error messages"
            style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5", resize: "vertical" }}
          />
          {form.formState.errors.description ? (
            <span style={{ color: "#ef4444" }}>{form.formState.errors.description.message}</span>
          ) : null}
        </label>
        {createTicket.isError ? (
          <div style={{ color: "#b91c1c", background: "#fee2e2", padding: "0.75rem", borderRadius: "0.75rem" }}>
            Failed to create ticket. Try again in a moment.
          </div>
        ) : null}
        <button
          type="submit"
          disabled={createTicket.isPending}
          style={{
            padding: "0.85rem 1.5rem",
            borderRadius: "0.85rem",
            border: "none",
            background: createTicket.isPending
              ? "linear-gradient(90deg, #94a3b8, #cbd5f5)"
              : "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            fontSize: "1rem",
            cursor: createTicket.isPending ? "not-allowed" : "pointer"
          }}
        >
          {createTicket.isPending ? "Submitting..." : "Submit ticket"}
        </button>
      </form>
    </div>
  );
}
