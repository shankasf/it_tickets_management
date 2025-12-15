"""
Ops / Analytics Agent (OpenAI Agents SDK)

Goal (from requirements):
- Answer admin questions about ticket volumes, SLAs, and trends.
- Translate natural language queries into aggregate queries:
  - e.g. open P1 tickets, tickets by category, SLA breaches (approximate via status/age).

This agent is primarily used by ADMIN (and optionally AGENT for simple lists).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from agents import (
    Agent,
    FunctionToolResult,
    ModelSettings,
    RunContextWrapper,
    ToolsToFinalOutputResult,
    function_tool,
)
from services.ticket_service import get_metrics, list_tickets


class Ticket(BaseModel):
    id: int
    title: str
    status: str
    priority: str
    category_id: int
    requester_id: int
    assignee_id: Optional[int] = None
    created_at: datetime


class MetricsResult(BaseModel):
    by_status: List[Dict[str, Any]]
    by_priority: List[Dict[str, Any]]
    by_category: List[Dict[str, Any]]


@function_tool()
def get_metrics_tool(
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
) -> MetricsResult:
    """
    Fetch aggregate metrics over tickets (by status, priority, category)
    for an optional created_at date range.
    """
    filters: Dict[str, Any] = {}
    if created_after is not None:
        filters["created_after"] = created_after
    if created_before is not None:
        filters["created_before"] = created_before
    data = get_metrics(filters)
    return MetricsResult(**data)


@function_tool()
def list_tickets_tool(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    requester_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> List[Ticket]:
    """
    List tickets with optional filters for use in admin/agent views.
    """
    filters: Dict[str, Any] = {"limit": limit, "offset": offset}
    if status is not None:
        filters["status"] = status
    if priority is not None:
        filters["priority"] = priority
    if assignee_id is not None:
        filters["assignee_id"] = assignee_id
    if requester_id is not None:
        filters["requester_id"] = requester_id
    if category_id is not None:
        filters["category_id"] = category_id
    if search:
        filters["search"] = search

    rows = list_tickets(filters)
    return [Ticket(**row) for row in rows]


async def ops_tool_use_behavior(
    context: RunContextWrapper[Any],
    results: List[FunctionToolResult],
) -> ToolsToFinalOutputResult:
    """
    Convert metrics/list results into concise, readable summaries.
    """
    if not results:
        return ToolsToFinalOutputResult(
            is_final_output=True,
            final_output="I couldn't retrieve analytics data due to a tool error.",
        )

    tool_result = results[0]
    output = tool_result.output

    if isinstance(output, MetricsResult):
        # Build a compact summary from metrics
        lines: List[str] = ["Ticket metrics overview:"]

        if output.by_status:
            parts = [f"{row.get('status')}: {row.get('count')}" for row in output.by_status]
            lines.append("By status: " + ", ".join(parts))

        if output.by_priority:
            parts = [f"{row.get('priority')}: {row.get('count')}" for row in output.by_priority]
            lines.append("By priority: " + ", ".join(parts))

        if output.by_category:
            parts = [f"{row.get('name')}: {row.get('count')}" for row in output.by_category]
            lines.append("By category: " + ", ".join(parts))

        return ToolsToFinalOutputResult(is_final_output=True, final_output="\n".join(lines))

    if isinstance(output, list) and output and isinstance(output[0], Ticket):
        tickets: List[Ticket] = output
        header = "Tickets (showing up to first {n}):".format(n=len(tickets))
        lines = [header]
        for t in tickets[:200]:
            lines.append(
                f"- #{t.id} [{t.status} {t.priority}] category={t.category_id} "
                f"req={t.requester_id} assignee={t.assignee_id or 'unassigned'}: {t.title}"
            )
        return ToolsToFinalOutputResult(is_final_output=True, final_output="\n".join(lines))

    return ToolsToFinalOutputResult(
        is_final_output=True,
        final_output=f"Analytics tool call completed. Result: {output}",
    )


ops_analytics_agent = Agent(
    name="ops_analytics_agent",
    instructions=(
        "You are the Ops/Analytics Agent for the IT helpdesk.\n"
        "- Your primary users are ADMIN (and sometimes AGENT) roles.\n"
        "- They will ask high-level questions about volumes, SLAs, and trends.\n\n"
        "When you need quantitative data:\n"
        "1) Decide on an appropriate date range and filters based on the question.\n"
        "2) For aggregated overviews (by status/priority/category), call get_metrics_tool.\n"
        "3) For specific queues or lists (e.g., 'my P1 tickets'), call list_tickets_tool\n"
        "   with suitable filters (status, priority, assignee_id, etc.).\n"
        "4) Present answers as concise text summaries; short bullet-style lines are fine.\n\n"
        "Important:\n"
        "- Do not expose raw SQL or internal implementation details.\n"
        "- Focus on clear counts, small breakdowns, and obvious next steps for admins.\n"
    ),
    tools=[get_metrics_tool, list_tickets_tool],
    tool_use_behavior=ops_tool_use_behavior,
    model_settings=ModelSettings(model="gpt-4o-mini", tool_choice=None),
    handoff_description=(
        "Specialized in answering admin/ops questions about ticket volumes, priorities, "
        "categories, and simple trends using aggregate metrics and ticket lists."
    ),
)


