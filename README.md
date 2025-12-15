## IT Helpdesk Multi‑Agent Chatbot

An internal IT ticketing chatbot built with a multi‑agent LLM backend, PostgreSQL, and a Streamlit UI.  
Requesters, agents, and admins can all use a chat interface to create, track, triage, and analyze IT tickets.

---

## High‑Level Overview

- **Frontend**: `app.py` – a Streamlit app providing:
  - Role selector: **Requester / Agent / Admin**
  - User selector backed by seeded users in the database
  - Chat interface that talks to the orchestrator each turn
  - Sidebar panel showing the **active ticket** and its **attachments**
- **Orchestrator**: `services/orchestrator.py`
  - Maintains per‑session state (`SessionState`)
  - Routes each user message to a specialist agent based on intent
  - Updates `active_ticket_id` and chat history
- **Agents (LLM‑powered)**: in `services/agents/`
  - `router_agent.py` – classifies intent using the LLM
  - `intake_agent.py` – creates new tickets
  - `status_agent.py` – status queries, comments, safe updates
  - `triage_agent.py` – agent‑side triage (category, priority, assignee)
  - `ops_analytics_agent.py` – admin analytics and ticket lists
- **Domain / Data layer**:
  - PostgreSQL schema in `database/schema.py`
  - Database wiring in `database/connection.py`
  - Seed scripts in `database/seed_data.py`
  - Ticket operations in `services/ticket_service.py`
  - Caching & simple services in `services/cache.py` and `services/user_service.py`
- **LLM Client**: `llm_client.py`
  - Thin wrapper around OpenAI’s chat completions API
  - Normalizes tool‑call responses for the router

---

## Project Structure

```text
.
├─ app.py                      # Streamlit UI entrypoint
├─ llm_client.py               # LLM wrapper (OpenAI Chat Completions)
├─ services/
│  ├─ orchestrator.py          # Session state + routing to specialist agents
│  ├─ ticket_service.py        # Ticket CRUD, comments, metrics, validations
│  ├─ user_service.py          # Simple user listing for UI
│  ├─ cache.py                 # In‑memory cache for teams/categories/SLA
│  └─ agents/
│     ├─ intake_agent.py       # New issue intake and ticket creation
│     ├─ status_agent.py       # Ticket status / updates / comments
│     ├─ triage_agent.py       # Agent triage: category/priority/assignee
│     ├─ ops_analytics_agent.py# Admin analytics / queue views
│     └─ router_agent.py       # Intent classification + ticket id hints
├─ database/
│  ├─ connection.py            # DB connection + schema init/reset helpers
│  ├─ schema.py                # SQL DDL: enums, tables, indexes, triggers
│  └─ seed_data.py             # Seeds teams, users, categories, SLAs, tickets
├─ uploads/                    # Ticket attachment uploads (created at runtime)
└─ requirements.txt            # Python dependencies
```

There is also an `Activity diagram.png` describing the high‑level flow of the system.

---

## Data Model (PostgreSQL)

Defined in `database/schema.py` and initialized via `database/connection.py`:

- **Enums**
  - `user_role_enum`: `REQUESTER`, `AGENT`, `ADMIN`
  - `ticket_status_enum`: `NEW`, `TRIAGED`, `IN_PROGRESS`, `WAITING_ON_REQUESTER`,
    `WAITING_ON_VENDOR`, `RESOLVED`, `CLOSED`, `REOPENED`
  - `priority_enum`: `P1`, `P2`, `P3`, `P4`
- **Core tables**
  - `teams` – IT teams (Service Desk, Network, etc.)
  - `users` – people using the system (requesters, agents, admins)
  - `categories` – ticket categories + default priority
  - `sla_policies` – SLA per priority (first response / resolution minutes)
  - `tickets` – main ticket table (status, priority, category, requester, assignee, SLA, due date)
  - `comments` – ticket comments (with `is_internal` for agent‑only notes)
  - `attachments` – file metadata linked to tickets
  - `audit_events` – history of ticket changes (status, assignee, priority, etc.)
- **Indexes & triggers**
  - Multiple indexes on status/priority/assignee/requester/created_at for fast queries
  - Trigger to automatically update `tickets.updated_at` on change

Seed data in `database/seed_data.py` populates:

- 3–5 **teams**
- 10–20 **users** (mix of Requesters, Agents, Admins)
- 6–10 **categories** (Access Request, Network Issue, Hardware Problem, etc.)
- **SLA policies** (Standard P1–P4)
- 20–30 **tickets** across various statuses and priorities
- Sample **comments** and **audit events** for realism

---

## Orchestrator & Agent Architecture

### Session State

`services/orchestrator.py` maintains a per‑session `SessionState`:

- `role`: `"REQUESTER" | "AGENT" | "ADMIN"`
- `user_id`: current signed‑in user
- `active_ticket_id`: the ticket currently in focus (if any)
- `history`: chat turn history (simple list of `{role, content}`)
- `last_intent`: last high‑level intent handled (`create_ticket`, `check_status`, etc.)

The orchestrator is **UI‑agnostic**; `app.py` simply passes in the current
state and the new user message to `orchestrate_turn()`.

### Turn Flow

For each user message:

1. **Route**:
   - Calls `router_agent.run_router()` (LLM via `llm_client.llm_complete`) to classify intent:
     - `create_ticket`, `check_status`, `add_info`, `agent_triage_help`,
       `list_tickets`, `admin_metrics`, or `small_talk`
   - Attempts to parse a `ticket_hint` (e.g., from “ticket #123”)
2. **Normalize intent**:
   - Applies some heuristics (e.g., “assign/reassign” forces `agent_triage_help`)
   - Handles confirmation flows (e.g., “yes, create this ticket”)
   - Enforces **role‑based permissions** via `_role_allows_intent`
3. **Dispatch**:
   - Chooses one of the specialist agents:
     - `intake_agent` for `create_ticket`
     - `status_agent` for `check_status` / `add_info`
     - `triage_agent` for `agent_triage_help`
     - `ops_analytics_agent` for `list_tickets` / `admin_metrics`
   - Builds an input prompt including:
     - User role, user id, active ticket id, router intent
     - Short summary of recent conversation history
4. **Run Agent**:
   - Uses the `agents.Runner` helper (`_run_agent`) to execute the chosen agent
   - Agents may call domain tools (`create_ticket`, `update_ticket`, `get_metrics`, etc.)
5. **Update State**:
   - Appends to both per‑session and per‑user global history
   - Attempts to extract a ticket id from the agent’s reply to update `active_ticket_id`

If the router yields `small_talk` or cannot match a clear intent, the orchestrator
returns a helpful fallback explanation of what the assistant can do.

---

## Specialist Agents

All agents live under `services/agents/` and are built using an Agents SDK that
wraps Python functions as typed tools (`@function_tool`) and manages tool use behavior.

- **Router Agent** – `router_agent.py`
  - Uses `llm_client.llm_complete` directly (no tools)
  - Input: user message prefixed with role + active ticket
  - Output: JSON `{"intent": ..., "ticket_hint": ...}`

- **Intake Agent** – `intake_agent.py`
  - Goal: turn free‑form issue descriptions into **structured tickets**
  - Tool: `create_ticket_tool` → `services.ticket_service.create_ticket`
  - Behavior:
    - Asks clarifying questions about impact, urgency, and affected system
    - Proposes title, category, priority
    - Explicitly asks for confirmation (yes/no) before calling `create_ticket`
    - On success, replies with a concise message like  
      `"Created ticket #123: Cannot connect to office Wi‑Fi (priority P2, category_id 4)."`

- **Status Agent** – `status_agent.py`
  - Tools:
    - `get_ticket_with_comments_tool`
    - `get_latest_ticket_for_requester_tool`
    - `add_comment_tool`
    - `update_ticket_tool`
  - Capabilities:
    - For **requesters**: check status, add comments, request close/reopen within allowed transitions
    - For **agents/admins**: change status/priority/assignee, add internal notes
    - Summarizes tickets with status, priority, assignee, due date, and last comment

- **Triage Agent** – `triage_agent.py`
  - Tools:
    - `get_ticket_tool`
    - `update_ticket_for_triage_tool`
  - Focused on **category, priority, and assignee** (not status)
  - Asks for explicit confirmation before applying triage changes
  - Summarizes triage details after update

- **Ops / Analytics Agent** – `ops_analytics_agent.py`
  - Tools:
    - `get_metrics_tool` → aggregates over tickets by status/priority/category
    - `list_tickets_tool` → filtered ticket lists
  - Used primarily by **admins** and sometimes agents for queue views
  - Produces compact textual summaries of metrics or ticket lists

---

## Streamlit UI (`app.py`)

Key behaviors:

- Sets wide layout and page title: **“IT Helpdesk Ticketing Chatbot”**
- **Sidebar – Session:**
  - Role select box (Requester / Agent / Admin)
  - User select box backed by `services.user_service.list_users`
  - Ensures `SessionState` is initialized or reset when the user changes
  - Optional categories reference using `services.cache.get_categories`
- **Sidebar – Active Ticket:**
  - Shows current `active_ticket_id` from `SessionState`
  - File uploader that:
    - Saves uploaded file to `uploads/`
    - Registers metadata via `services.ticket_service.add_attachment`
  - Shows existing attachments for the active ticket via `list_attachments`
- **Main Chat Area:**
  - Renders prior messages from `SessionState.history`
  - Reads new input using `st.chat_input`
  - Calls `orchestrate_turn(prompt, ss)` (async via `asyncio.run`)
  - Updates `st.session_state.session_state` with the new state

The UI is intentionally thin and delegates logic to the orchestrator and agents.

---

## LLM Client (`llm_client.py`)

`llm_client.llm_complete` is a reusable wrapper around the OpenAI Chat Completions API:

- Takes:
  - `system_prompt`: system message for behavior
  - `messages`: list of `{role, content}` chat messages
  - Optional tool specifications
- Adds the system prompt as the first message
- Configurable:
  - `model` (default: `gpt-4o-mini`)
  - `temperature`, `max_tokens`, `timeout`, `retry`
- Returns:
  - `"content"`: model’s textual reply
  - `"tool_calls"`: normalized list of tool invocations (if any)

You can swap the underlying model/provider by changing `model` and the `OpenAI` client
initialization; the rest of the code calls only this wrapper.

---

## Setup & Configuration

### Prerequisites

- Python 3.10+ recommended
- PostgreSQL database accessible from your environment
- A valid OpenAI API key (for the current `llm_client.py` implementation)

### Environment Variables

The project uses `python-dotenv` and expects a `.env` file (or environment) with:

- **Database**
  - `DB_HOST`
  - `DB_PORT`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_NAME`
- **LLM**
  - `OPENAI_API_KEY`

Example `.env` (adjust values as needed):

```env
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=helpdesk_db

OPENAI_API_KEY=sk-...
```

### Install Python Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

*(This is documentation; you can run installation commands in your own environment.)*

---

## Initializing and Seeding the Database

1. **Test DB connection and initialize schema**

   You can use the helpers in `database/connection.py`:

   - `test_connection()` – verifies that the connection is valid
   - `init_database(drop_existing=False)` – creates enums, tables, indexes, triggers

2. **Seed reference and demo data**

   Run `database/seed_data.py` as a script to populate teams, users, categories,
   SLA policies, tickets, comments, and audit events.

This gives you a realistic dataset for demoing the chatbot and exploring metrics.

---

## Running the App

From the project root:

```bash
streamlit run app.py
```

Then open the Streamlit URL in a browser. Typical flow:

- Select a **role** and **user** from the sidebar
- As a **Requester**:
  - Describe a new issue (the Intake Agent will ask clarifying questions and create a ticket)
  - Ask “What is the status of my ticket?” or “What about ticket #123?”
  - Add more information to an existing ticket
- As an **Agent**:
  - Ask for triage help (“Help me triage ticket #123” or “assign/reassign this ticket”)
  - Add internal notes and update status/priority/assignee
- As an **Admin**:
  - Ask for queue overviews and metrics (“How many P1 tickets are open?”, “Show tickets by category”)

---

## Extending the System

- **New intents or routing rules**
  - Update `INTENTS` and `ROUTER_SYSTEM_PROMPT` in `services/agents/router_agent.py`
  - Add any new high‑level intents to `_role_allows_intent` in `services/orchestrator.py`
- **New specialist agent**
  - Implement a new `Agent` in `services/agents/` with appropriate tools
  - Wire it into `orchestrator.orchestrate_turn()` based on new intents
- **Additional domain logic**
  - Extend `services/ticket_service.py` for new operations
  - Add functions in `services/cache.py` and `services/user_service.py` as needed

Because the orchestrator is the only component the UI talks to, most changes can
be made in the agent and service layers without touching the frontend.

---

## Notes

- Attachments are stored on disk under `uploads/` with metadata in the database.
- Role‑based status transitions and validations are enforced in `services/ticket_service.py`.
- Logging is enabled across services and the seed script to help with debugging and demos.


