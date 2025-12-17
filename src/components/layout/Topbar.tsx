import { FormEvent, useState } from "react";
import { useAuth } from "../../app/providers/AuthProvider";
import type { UserRole } from "../../types/auth";
import "./topbar.css";

const roleOptions: Array<{ value: UserRole; label: string }> = [
  { value: "requester", label: "Requester" },
  { value: "agent", label: "Agent" },
  { value: "admin", label: "Admin" }
];

export function Topbar() {
  const { user, loginAs } = useAuth();
  const [search, setSearch] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    // Placeholder for real search logic once backend is connected.
    console.info("Search submitted", search);
  };

  return (
    <header className="app-topbar">
      <form className="app-topbar__search" onSubmit={handleSubmit} role="search">
        <input
          aria-label="Search tickets"
          placeholder="Search tickets, users, or assets..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </form>
      <div className="app-topbar__actions">
        <select
          aria-label="Switch role"
          className="app-topbar__role-switch"
          value={user?.role ?? "requester"}
          onChange={(event) => loginAs(event.target.value as UserRole)}
        >
          {roleOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="app-topbar__user">
          <strong>{user?.name ?? "Guest"}</strong>
          <span>{user?.email ?? "Not signed in"}</span>
        </div>
      </div>
    </header>
  );
}
