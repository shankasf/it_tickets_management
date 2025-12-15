"""
Triage Agent (OpenAI Agents SDK)

Goal (from requirements):
- Help IT agents triage existing tickets.
- Given a ticket id or description, propose:
  - Category
  - Priority (P1–P4)
  - Suggested assignee/team
- On explicit agent approval, call update_ticket() to persist changes.

This agent assumes:
- It is used primarily by users with role AGENT (or ADMIN for overrides).
- The orchestrator provides context (role, user_id, active_ticket_id) inline.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    ToolsToFinalOutputResult,
    function_tool,
)
from services.ticket_service import get_ticket, update_ticket


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


@function_tool()
def get_ticket_tool(ticket_id: int) -> Ticket:
    """
    Fetch a single ticket by id for triage purposes.
    """
    data = get_ticket(ticket_id)
    if not data:
        raise ValueError(f"Ticket with id={ticket_id} not found")
    return Ticket(**data)


@function_tool()
def update_ticket_for_triage_tool(
    ticket_id: int,
    actor_role: str,
    actor_id: int,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
) -> Ticket:
    """
    Update triage-related fields (category, priority, assignee) on a ticket.

    - actor_role should usually be 'AGENT' or 'ADMIN'.
    - The underlying domain function enforces role-based rules & validation.
    """
    patch: dict[str, Any] = {}
    if category_id is not None:
        patch["category_id"] = category_id
    if priority is not None:
        patch["priority"] = priority
    if assignee_id is not None:
        patch["assignee_id"] = assignee_id

    updated = update_ticket(ticket_id, patch, actor_role=actor_role, actor_id=actor_id)
    return Ticket(**updated)


async def triage_tool_use_behavior(
    context: RunContextWrapper[Any],
    results: list[FunctionToolResult],
) -> ToolsToFinalOutputResult:
    """
    Turn tool outputs into a short, triage-focused response.
    """
    if not results:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output="I tried to look up or update that ticket, but the tools did not return any result.",
        )

    tool_result = results[0]
    output = tool_result.output

    if isinstance(output, Ticket):
        ticket = output
        msg = (
            f"Triage details for ticket #{ticket.id}: {ticket.title}\n"
            f"- Status: {ticket.status}\n"
            f"- Priority: {ticket.priority}\n"
            f"- Category ID: {ticket.category_id}\n"
            f"- Assignee: {ticket.assignee_id or 'unassigned'}\n"
        )
        return ToolsToFinalOutputResult(is_final_output=True, final_output=msg)

    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=f"Triage tool call completed. Result: {output}",
    )


triage_agent = Agent(
    name="triage_agent",
    instructions=(
        "You are the Triage Agent for the IT helpdesk.\n"
        "- Your primary users are AGENT and ADMIN roles.\n"
        "- They will ask for help triaging existing tickets by id.\n\n"
        "When helping with a ticket:\n"
        "1) If you don't have the full ticket details yet, call get_ticket_tool with the ticket_id.\n"
        "2) Based on the description and context, propose a category_id, priority (P1–P4), and assignee_id.\n"
        "3) Clearly explain your reasoning in natural language, but keep it brief.\n"
        "4) Ask for explicit confirmation before changing anything, for example:\n"
        "   'Should I update this ticket to P2 and assign it to Network Team (user 7)?'.\n"
        "5) Only after the user confirms, call update_ticket_for_triage_tool with the chosen values\n"
        "   and the actor's role/id as provided in the context.\n\n"
        "Important:\n"
        "- Never change ticket status; focus on category, priority, and assignee only.\n"
        "- Respect the constraints of the underlying domain rules; if an update fails, explain why.\n"
    ),
    tools=[get_ticket_tool, update_ticket_for_triage_tool],
    tool_use_behavior=triage_tool_use_behavior,
    model_settings=ModelSettings(model="gpt-4o-mini", tool_choice=None),
    handoff_description=(
        "Specialized in analyzing existing tickets and suggesting or applying triage updates "
        "(category, priority, assignee) for IT agents."
    ),
)


