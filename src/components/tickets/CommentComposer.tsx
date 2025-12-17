import { FormEvent, useState } from "react";

interface CommentComposerProps {
  onSubmit: (input: { body: string; isInternal: boolean }) => void;
  disabled?: boolean;
  allowInternal?: boolean;
}

export function CommentComposer({ onSubmit, disabled = false, allowInternal = false }: CommentComposerProps) {
  const [body, setBody] = useState("");
  const [isInternal, setInternal] = useState(false);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!body.trim()) return;
    onSubmit({ body: body.trim(), isInternal: isInternal && allowInternal });
    setBody("");
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        display: "grid",
        gap: "0.75rem",
        background: "#f8fafc",
        padding: "1.25rem",
        borderRadius: "0.9rem",
        border: "1px solid #e2e8f0"
      }}
    >
      <textarea
        value={body}
        onChange={(event) => setBody(event.target.value)}
        placeholder="Add an update or request more info"
        rows={4}
        style={{ padding: "0.75rem", borderRadius: "0.75rem", border: "1px solid #cbd5f5", resize: "vertical" }}
        disabled={disabled}
      />
      <div style={{ display: "flex", gap: "1rem", alignItems: "center", justifyContent: "space-between" }}>
        {allowInternal ? (
          <label style={{ display: "flex", gap: "0.5rem", alignItems: "center", color: "#475569" }}>
            <input
              type="checkbox"
              checked={isInternal}
              onChange={(event) => setInternal(event.target.checked)}
              disabled={disabled}
            />
            Internal note
          </label>
        ) : (
          <span style={{ color: "#94a3b8", fontSize: "0.9rem" }}>Requester will be notified</span>
        )}
        <button
          type="submit"
          disabled={disabled || !body.trim()}
          style={{
            padding: "0.6rem 1.2rem",
            borderRadius: "0.85rem",
            border: "none",
            background: disabled || !body.trim() ? "#cbd5f5" : "linear-gradient(90deg, #2563eb, #38bdf8)",
            color: "#ffffff",
            fontWeight: 600,
            cursor: disabled || !body.trim() ? "not-allowed" : "pointer"
          }}
        >
          Post update
        </button>
      </div>
    </form>
  );
}
