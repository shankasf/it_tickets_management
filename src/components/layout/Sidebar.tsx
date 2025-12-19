import { NavLink } from "react-router-dom";
import "./sidebar.css";

const mainLinks = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/tickets", label: "Tickets" },
  { to: "/my-tickets", label: "My Tickets" },
  { to: "/reports", label: "Reports" },
   { to: "/Giga", label: "Giga" }
];

const adminLinks = [
  { to: "/admin", label: "Admin Overview" },
  { to: "/admin/users", label: "Users & Roles" },
  { to: "/admin/teams", label: "Teams" },
  { to: "/admin/categories", label: "Categories" },
  { to: "/admin/sla", label: "SLA Policies" }
];

export function Sidebar() {
  return (
    <aside className="app-sidebar">
      <div className="app-sidebar__brand">IT Service Desk</div>
      <nav className="app-sidebar__nav">
        {mainLinks.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              isActive
                ? "app-sidebar__link app-sidebar__link--active"
                : "app-sidebar__link"
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div>
        <p className="app-sidebar__section">Administration</p>
        <nav className="app-sidebar__nav">
          {adminLinks.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                isActive
                  ? "app-sidebar__link app-sidebar__link--active"
                  : "app-sidebar__link"
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  );
}
