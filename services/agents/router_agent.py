"""
Router "agent" using the llm_client thin wrapper.

- Purpose: classify user intent and surface an optional ticket hint.
- No tools; no function calls. The orchestrator dispatches to specialized agents.
- Output shape: {"intent": "<intent>", "ticket_hint": <int|null>}
"""

import json
import re
from typing import Optional, List, Dict, Any

from llm_client import llm_complete as _llm_complete

INTENTS = [
    "create_ticket",
    "check_status",
    "add_info",
    "agent_triage_help",
    "list_tickets",
    "admin_metrics",
    "small_talk",
]

def _extract_ticket_id(text: str) -> Optional[int]:
    m = re.search(r"(?:#|ticket\s+)(\d+)", text, re.IGNORECASE)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


ROUTER_SYSTEM_PROMPT = (
    "You are a routing component for an IT helpdesk chatbot.\n"
    f"Choose exactly one intent from: {', '.join(INTENTS)}.\n"
    "Rules:\n"
    "- If unclear or chatting, use 'small_talk'.\n"
    "- If asking ticket status, use 'check_status'.\n"
    "- If providing more info on an existing issue, use 'add_info'.\n"
    "- If an agent asks triage help, use 'agent_triage_help'.\n"
    "- If the user asks to assign/reassign a ticket, use 'agent_triage_help'.\n"
    "- If an agent asks for queues/lists, use 'list_tickets'.\n"
    "- If an admin asks for metrics/volumes/SLA, use 'admin_metrics'.\n"
    "- Else, if describing a new issue, use 'create_ticket'.\n"
    "Also detect a ticket id if mentioned (e.g., '#123' or 'ticket 123').\n"
    "OUTPUT ONLY compact JSON with keys intent and ticket_hint (int or null).\n"
    'Example: {\"intent\": \"check_status\", \"ticket_hint\": 123}\n'
)

async def run_router(user_message: str, role: str, active_ticket_id: Optional[int] = None) -> dict:
    """
    Calls the router via llm_client and returns {"intent": str, "ticket_hint": Optional[int]}.
    """
    # Provide role + active ticket context inline to the model
    prefixed = f"Role: {role}. Active ticket: {active_ticket_id or 'none'}. Message: {user_message}"

    resp = _llm_complete(
        system_prompt=ROUTER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prefixed}],
        tools=None,
    )

    raw_output = resp.get("content", "") or ""

    # Try to parse JSON; fallback to small_talk
    try:
        parsed = json.loads(raw_output)
        intent = parsed.get("intent", "small_talk")
        ticket_hint = parsed.get("ticket_hint", None)
        if isinstance(ticket_hint, str) and ticket_hint.isdigit():
            ticket_hint = int(ticket_hint)
        if intent not in INTENTS:
            intent = "small_talk"
        return {"intent": intent, "ticket_hint": ticket_hint or active_ticket_id}
    except Exception:
        # Heuristic fallback
        fallback_intent = "small_talk"
        ticket_hint = _extract_ticket_id(raw_output) or active_ticket_id
        # rough heuristic for status/add_info/create
        lower = raw_output.lower()
        if "last ticket" in lower:
            return {"intent": "check_status", "ticket_hint": ticket_hint}
        if "assign" in lower or "reassign" in lower:
            return {"intent": "agent_triage_help", "ticket_hint": ticket_hint}
        if any(k in lower for k in ["status", "update", "progress"]):
            fallback_intent = "check_status"
        elif any(k in lower for k in ["more info", "additional", "attach", "screenshot", "log"]):
            fallback_intent = "add_info"
        elif any(k in lower for k in ["issue", "problem", "error", "not working", "help"]):
            fallback_intent = "create_ticket"
        return {"intent": fallback_intent, "ticket_hint": ticket_hint}