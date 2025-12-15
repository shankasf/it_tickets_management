"""
Status Agent (OpenAI Agents SDK)

Goal (from requirements):
- Handle queries about ticket status and updates.
- Parse ticket reference (ID or “my last ticket,” “VPN ticket”) – the LLM handles this reasoning.
- Resolve to a specific ticket (the orchestrator may help by passing context like active_ticket_id).
- Call get_ticket_with_comments() and summarize: status, assignee, last update, SLA risk.
- For requesters: allow adding comments and requesting close/reopen, respecting allowed transitions.
- For agents/admins: allow updating status/priority/assignee.

This file defines:
- @function_tool wrappers around:
  - get_ticket_with_comments()
  - add_comment()
  - update_ticket()
- A Status Agent that uses those tools and produces concise, user‑friendly responses.

The router/orchestrator is responsible for:
- Deciding WHEN to call this agent.
- Providing user context such as:
  - role: REQUESTER / AGENT / ADMIN
  - user_id: int
  - (optionally) active_ticket_id: int
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    ToolsToFinalOutputFunction,
    ToolsToFinalOutputResult,
    function_tool,
)
from services.ticket_service import (
    add_comment,
    get_ticket_with_comments,
    update_ticket,
    list_tickets,
)


class Comment(BaseModel):
    id: int
    ticket_id: int
    author_id: int
    body: str
    is_internal: bool
    created_at: datetime


class Ticket(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    category_id: int
    requester_id: int
    assignee_id: Optional[int] = None
    sla_policy_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    due_at: Optional[datetime] = None


class TicketWithComments(Ticket):
    comments: List[Comment] = []


@function_tool()
def get_ticket_with_comments_tool(ticket_id: int, user_role: str) -> TicketWithComments:
    """
    Domain-wrapped tool: fetch a ticket and its comments from the database using
    get_ticket_with_comments(). The user_role is used to determine whether internal
    comments should be included (AGENT/ADMIN) or hidden (REQUESTER).
    """
    data = get_ticket_with_comments(ticket_id, user_role=user_role)
    if not data:
        raise ValueError(f"Ticket with id={ticket_id} not found")

    raw_comments = data.pop("comments", []) or []
    comments = [Comment(**c) for c in raw_comments]
    return TicketWithComments(**data, comments=comments)


@function_tool()
def get_latest_ticket_for_requester_tool(requester_id: int, user_role: str) -> TicketWithComments:
    """
    Helper tool: find the most recent ticket for a requester and return it with comments.

    Used for queries like "my last ticket" when no explicit ticket id is provided.
    """
    # Get most recent ticket for this requester
    rows = list_tickets({"requester_id": requester_id, "limit": 1})
    if not rows:
        raise ValueError(f"No tickets found for requester_id={requester_id}")

    ticket_row = rows[0]
    ticket_id = ticket_row["id"]

    data = get_ticket_with_comments(ticket_id, user_role=user_role)
    if not data:
        raise ValueError(f"Ticket with id={ticket_id} not found")

    raw_comments = data.pop("comments", []) or []
    comments = [Comment(**c) for c in raw_comments]
    return TicketWithComments(**data, comments=comments)


@function_tool()
def add_comment_tool(
    ticket_id: int,
    author_id: int,
    body: str,
    is_internal: bool = False,
) -> Comment:
    """
    Domain-wrapped tool: add a comment to the ticket using add_comment().
    """
    payload = {
        "author_id": author_id,
        "body": body,
        "is_internal": is_internal,
    }
    comment_dict = add_comment(ticket_id, payload)
    return Comment(**comment_dict)


@function_tool()
def update_ticket_tool(
    ticket_id: int,
    actor_role: str,
    actor_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    sla_policy_id: Optional[int] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Ticket:
    """
    Domain-wrapped tool: update fields on an existing ticket using update_ticket().

    The underlying domain function enforces:
    - Role-based, legal status transitions.
    - Priority / assignee / SLA validation.
    """
    patch: dict[str, Any] = {}
    if status is not None:
        patch["status"] = status
    if priority is not None:
        patch["priority"] = priority
    if assignee_id is not None:
        patch["assignee_id"] = assignee_id
    if sla_policy_id is not None:
        patch["sla_policy_id"] = sla_policy_id
    if title is not None:
        patch["title"] = title
    if description is not None:
        patch["description"] = description

    updated_dict = update_ticket(ticket_id, patch, actor_role=actor_role, actor_id=actor_id)
    return Ticket(**updated_dict)


async def status_tool_use_behavior(
    context: RunContextWrapper[Any],
    results: list[FunctionToolResult],
) -> ToolsToFinalOutputResult:
    """
    Convert tool outputs into a clear final answer for the user.

    We primarily expect three tool types:
    - get_ticket_with_comments_tool -> TicketWithComments
    - add_comment_tool -> Comment
    - update_ticket_tool -> Ticket

    The LLM handles deciding when to call which tool; this function focuses on
    human-readable summaries.
    """
    if not results:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output="I tried to look up your ticket, but something went wrong while calling the tools.",
        )

    tool_result = results[0]  # The current SDK typically calls one tool at a time for this agent.
    output = tool_result.output

    # Ticket with comments: summarize status, assignee, last update, and recent comments
    if isinstance(output, TicketWithComments):
        ticket = output
        last_comment_text = ""
        if ticket.comments:
            last_comment = ticket.comments[-1]
            last_comment_text = f"Last update on {last_comment.created_at:%Y-%m-%d %H:%M}: {last_comment.body}"

        assignee_str = f"assigned to user #{ticket.assignee_id}" if ticket.assignee_id else "not yet assigned"
        due_str = f", due by {ticket.due_at:%Y-%m-%d %H:%M}" if ticket.due_at else ""

        summary_lines = [
            f"Ticket #{ticket.id}: {ticket.title}",
            f"- Status: {ticket.status}",
            f"- Priority: {ticket.priority}",
            f"- Category ID: {ticket.category_id}",
            f"- {assignee_str}{due_str}",
        ]
        if last_comment_text:
            summary_lines.append(f"- {last_comment_text}")

        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output="\n".join(summary_lines),
        )

    # Comment creation: confirm to the user
    if isinstance(output, Comment):
        comment = output
        visibility = "internal note" if comment.is_internal else "comment"
        msg = (
            f"Added a new {visibility} to ticket #{comment.ticket_id} "
            f"at {comment.created_at:%Y-%m-%d %H:%M}."
        )
        return ToolsToFinalOutputResult(is_final_output=True, final_output=msg)

    # Ticket update (status/priority/assignee/etc.): summarize key fields
    if isinstance(output, Ticket):
        ticket = output
        assignee_str = f"assigned to user #{ticket.assignee_id}" if ticket.assignee_id else "not yet assigned"
        msg = (
            f"Updated ticket #{ticket.id}: status={ticket.status}, "
            f"priority={ticket.priority}, {assignee_str}."
        )
        return ToolsToFinalOutputResult(is_final_output=True, final_output=msg)

    # Fallback: just stringify the output
    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=f"Tool call completed. Result: {output}",
    )


status_agent = Agent(
    name="status_agent",
    instructions=(
        "You are the Status Agent for an internal IT helpdesk.\n"
        "- Your job is to help users understand the status and history of their tickets,\n"
        "  and to perform safe updates via the provided tools.\n\n"
        "Core capabilities:\n"
        "1) Ticket lookup and summarization:\n"
        "   - When the user asks about a specific ticket (e.g., 'ticket #1234', 'my Wi‑Fi ticket'),\n"
        "     resolve which ticket they mean and call get_ticket_with_comments_tool.\n"
        "   - When the user says 'my last ticket' and no id is given, call\n"
        "     get_latest_ticket_for_requester_tool with the current requester_id and user_role.\n"
        "   - Summarize status, assignee, last update, and any important comments.\n"
        "2) Adding comments:\n"
        "   - When the user provides new information or follow-up, call add_comment_tool\n"
        "     with author_id set to the current user and is_internal set appropriately\n"
        "     (requesters create non-internal comments; agents/admins may create internal notes).\n"
        "3) Status/field updates:\n"
        "   - When the user explicitly requests a status change or similar update, call\n"
        "     update_ticket_tool with actor_role and actor_id provided by context.\n"
        "   - The domain layer will enforce legal transitions; if an update fails, explain why\n"
        "     in plain language.\n\n"
        "Role-specific behavior:\n"
        "- REQUESTER:\n"
        "  - May close their own RESOLVED tickets or request to reopen CLOSED ones.\n"
        "  - Should not see internal comments; rely on get_ticket_with_comments_tool for filtering.\n"
        "- AGENT:\n"
        "  - May transition NEW → TRIAGED → IN_PROGRESS → RESOLVED and set waiting statuses.\n"
        "  - May add internal notes that requesters cannot see.\n"
        "- ADMIN:\n"
        "  - May override any status; use this power carefully and keep explanations short.\n\n"
        "Important:\n"
        "- Always confirm destructive or significant changes (like closing or reopening a ticket)\n"
        "  in natural language before calling update_ticket_tool.\n"
        "- Keep responses concise and focused on status, next steps, and any deadlines or risks.\n"
    ),
    tools=[get_ticket_with_comments_tool, get_latest_ticket_for_requester_tool, add_comment_tool, update_ticket_tool],
    tool_use_behavior=status_tool_use_behavior,
    model_settings=ModelSettings(model="gpt-4o-mini", tool_choice=None),
    handoff_description=(
        "Specialized in looking up ticket state, summarizing history, and applying safe\n"
        "status/field updates (including comments) for requesters, agents, and admins."
    ),
)


