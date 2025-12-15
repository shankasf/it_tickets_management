"""
Intake Agent (OpenAI Agents SDK)

Goal (from requirements):
- Turn free-form issue descriptions into structured tickets.
- Ask clarifying questions: impact (one vs many), urgency, system/app affected.
- Infer candidate category and priority using LLM.
- Propose a ticket draft: title, description, category, priority.
- On confirmation, call create_ticket() and persist.
- Return ticket ID and a human-readable summary to the user.

This file defines:
- A @function_tool wrapper for the domain-level create_ticket()
- An Agent that uses that tool to actually create tickets.

The router/orchestrator decides WHEN to call this agent; the Intake agent itself
handles the multi-turn conversation and the final tool call.
"""

from typing import Any, Optional

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    Runner,
    ToolsToFinalOutputFunction,
    ToolsToFinalOutputResult,
    function_tool,
)
from services.ticket_service import create_ticket
from pydantic import BaseModel

class Ticket(BaseModel):
    id: int
    title: str
    description: str
    category_id: int
    priority: str
    requester_id: int
    assignee_id: Optional[int] = None
    sla_policy_id: Optional[int] = None
    initial_comment: Optional[str] = None



@function_tool()
def create_ticket_tool(
    title: str,
    description: str,
    category_id: Optional[int] = None,
    priority: Optional[str] = None,
    requester_id: Optional[int] = None,
    assignee_id: Optional[int] = None,
    sla_policy_id: Optional[int] = None,
    initial_comment: Optional[str] = None,
):
    """
    Domain-wrapped tool: creates a ticket in the database using the existing
    create_ticket() domain function. Returns the created ticket record.
    """
    # Basic defaults/fallbacks to reduce tool-call failures
    from services.cache import get_categories

    categories = get_categories()
    fallback_category_id = categories[0]["id"] if categories else 1

    payload = {
        "title": title,
        "description": description,
        "category_id": category_id or fallback_category_id,
        "priority": (priority or "P3").upper(),
        "requester_id": requester_id,
        "assignee_id": assignee_id,
        "sla_policy_id": sla_policy_id,
    }
    # Only include initial_comment if explicitly provided
    if initial_comment:
        payload["initial_comment"] = initial_comment
    ticket_dict = create_ticket(payload)
    return Ticket(**ticket_dict)

async def intake_tool_use_behavior(
    context: RunContextWrapper[Any],
    results: list[FunctionToolResult],
) -> ToolsToFinalOutputResult:
    """
    When the Intake agent calls create_ticket_tool, use the created Ticket
    to produce a clear, final response for the user.
    """
    if not results:
        return ToolsToFinalOutputResult(is_final_output=True, final_output="Something went wrong creating your ticket.")

    # We expect exactly one tool result here:
    ticket: Ticket = results[0].output  # thanks to Pydantic typing

    msg = (
        f"Created ticket #{ticket.id}: {ticket.title} "
        f"(priority {ticket.priority}, category_id {ticket.category_id})."
    )
    return ToolsToFinalOutputResult(is_final_output=True, final_output=msg)

intake_agent = Agent(
    name="intake_agent",
    instructions=(
        "You are the Intake Agent for an internal IT helpdesk.\n"
        "- The user will describe issues in natural language.\n"
        "- Your job is to gather missing details and create a structured ticket.\n\n"
        "Follow this process:\n"
        "1) Ask clarifying questions as needed, especially about:\n"
        "   - Impact: is this affecting one user or many?\n"
        "   - Urgency: how urgent is it (e.g., blocking work or minor)?\n"
        "   - System/app affected: VPN, Wi‑Fi, specific app, hardware, etc.\n"
        "2) Infer a good title, category_id, and priority:\n"
        "   - Title: short summary (e.g., 'Cannot connect to office Wi‑Fi').\n"
        "   - Priority: map impact/urgency to P1–P4 (P1 = critical, P4 = low).\n"
        "   - Category_id will be provided to you by the orchestrator or via prior context; "
        "     if not, propose a reasonable category and clearly mention it in your text.\n"
        "3) Propose a ticket draft to the user with:\n"
        "   - Title\n"
        "   - Description\n"
        "   - Category (by name or id if known)\n"
        "   - Priority\n"
        "4) Ask for explicit confirmation in the SAME turn: e.g., 'Should I create this ticket now? (yes/no)'.\n"
        "5) DO NOT call the create_ticket_tool until the user explicitly confirms with yes/yeah/sure/ok/please do.\n"
        "   If the user is unclear, ask again for a yes/no confirmation.\n"
        "6) ONLY after the user confirms, call the create_ticket_tool function tool "
        "with the appropriate arguments (title, description, category_id, priority, requester_id, etc.).\n"
        "7) After the tool returns, reply with the new ticket id and a clear summary, e.g.:\n"
        "   'Created ticket #1234: Cannot connect to office Wi‑Fi (P2, Network)'.\n\n"
        "Important:\n"
        "- Never call create_ticket_tool without confirmation.\n"
        "- Do not create duplicate tickets if the user says they already have one; in that case, "
        "you should defer to the Status Agent instead (this will be handled by the router/orchestrator).\n"
        "- Keep your questions and responses concise and user-friendly.\n"
    ),
    tools=[create_ticket_tool],
    tool_use_behavior=intake_tool_use_behavior,
    model_settings=ModelSettings(model="gpt-4o-mini", tool_choice=None),
    handoff_description=(
        "Specialized in onboarding new IT issues and creating tickets after "
        "asking clarifying questions and confirming with the user."
    ),
)