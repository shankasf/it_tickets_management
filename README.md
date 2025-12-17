# IT Issue Ticket Management Dashboard

React + TypeScript dashboard prototype for an IT helpdesk ticketing workflow. The UI demonstrates a modular, role-aware experience for requesters, agents, and admins, including ticket queues, ticket detail workflow, KPI dashboards, and administration pages.

## Getting Started

Install dependencies:

```bash
npm install
```

Run the development server:

```bash
npm run dev
```

Build for production:

```bash
npm run build
```

Run linting:

```bash
npm run lint
```

## Project Highlights

- **Role-aware routing** with auth and role guards for requester, agent, and admin experiences.
- **Ticket lifecycle UI** with list filters, detail views, status transitions, and comment workflows.
- **React Query** powered data layer with optimistic invalidation and modular hooks.
- **Form validation** via React Hook Form + Zod for ticket creation.
- **Reusable components** for layout, status, priority, charts, and dashboards.

## Next Steps

- Connect UI with a real backend API.
