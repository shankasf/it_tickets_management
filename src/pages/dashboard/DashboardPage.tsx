import { KpiCard } from "../../components/dashboard/KpiCard";
import { TicketsByCategoryChart } from "../../components/dashboard/TicketsByCategoryChart";
import { TrendsChart } from "../../components/dashboard/TrendsChart";

export function DashboardPage() {
  return (
    <div style={{ display: "grid", gap: "2rem" }}>
      <header style={{ display: "grid", gap: "0.5rem" }}>
        <h1 style={{ fontSize: "2rem", color: "#0f172a" }}>Service Desk Overview</h1>
        <p style={{ color: "#475569" }}>
          Track workload, SLA risk, and the queue health across your support organization.
        </p>
      </header>
      <section
        style={{
          display: "grid",
          gap: "1.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))"
        }}
      >
        <KpiCard title="Open tickets" value="128" description="Across all teams" />
        <KpiCard title="SLA at risk" value="14" description="Tickets within 8 hours of breach" />
        <KpiCard title="Avg first response" value="1.8h" description="Last 7 days" />
        <KpiCard title="Avg resolution" value="12.4h" description="Closed in last 30 days" />
      </section>
      <section
        style={{
          display: "grid",
          gap: "1.5rem",
          gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))"
        }}
      >
        <TicketsByCategoryChart />
        <TrendsChart />
      </section>
    </div>
  );
}
