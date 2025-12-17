import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "../../components/layout/Layout";
import { LoginPage } from "../../pages/auth/LoginPage";
import { DashboardPage } from "../../pages/dashboard/DashboardPage";
import { AdminLandingPage } from "../../pages/admin/AdminLandingPage";
import { AdminCategoriesPage } from "../../pages/admin/AdminCategoriesPage";
import { AdminSlaPage } from "../../pages/admin/AdminSlaPage";
import { AdminUsersPage } from "../../pages/admin/AdminUsersPage";
import { AdminTeamsPage } from "../../pages/admin/AdminTeamsPage";
import { ReportsPage } from "../../pages/reports/ReportsPage";
import { TicketDetailsPage } from "../../pages/tickets/TicketDetailsPage";
import { TicketsPage } from "../../pages/tickets/TicketsPage";
import { NewTicketPage } from "../../pages/tickets/NewTicketPage";
import { MyTicketsPage } from "../../pages/tickets/MyTicketsPage";
import { NotFoundPage } from "../../pages/NotFoundPage";
import { RequireAuth } from "./RequireAuth";
import { RequireRole } from "./RequireRole";

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<RequireAuth />}>
          <Route element={<Layout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="tickets">
              <Route index element={<TicketsPage />} />
              <Route path="new" element={<NewTicketPage />} />
              <Route path=":ticketId" element={<TicketDetailsPage />} />
            </Route>
            <Route path="my-tickets" element={<MyTicketsPage />} />
            <Route element={<RequireRole allowed={["agent", "admin"]} />}>
              <Route path="reports" element={<ReportsPage />} />
            </Route>
            <Route element={<RequireRole allowed={["admin"]} />}>
              <Route path="admin" element={<AdminLandingPage />} />
              <Route path="admin/users" element={<AdminUsersPage />} />
              <Route path="admin/teams" element={<AdminTeamsPage />} />
              <Route path="admin/categories" element={<AdminCategoriesPage />} />
              <Route path="admin/sla" element={<AdminSlaPage />} />
            </Route>
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
