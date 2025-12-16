"""
Simple multi-agent orchestrator.

Responsibilities (from requirements/plan):
- Maintain per-session state:
  - role: REQUESTER / AGENT / ADMIN
  - user_id: int
  - active_ticket_id: Optional[int]
  - history: simple message log (optional, for UI/debug)
- On each user message:
  1) Call RouterAgent to classify intent + optional ticket hint.
  2) Choose the appropriate specialist agent (Intake / Status / Triage / OpsAnalytics).
  3) Call that agent with a context-prefixed message.
  4) Update state (especially active_ticket_id) and return the assistant reply.

This module is UI-agnostic; Streamlit or any other frontend can call
`orchestrate_turn()` with the current session state.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from agents import ItemHelpers, MessageOutputItem, Runner

from services.agents.intake_agent import intake_agent
from services.agents.status_agent import status_agent
from services.agents.triage_agent import triage_agent
from services.agents.ops_analytics_agent import ops_analytics_agent
from services.agents.router_agent import run_router
from llm_client import llm_complete

# Per-user conversation memory (process-local)
_USER_HISTORY: Dict[int, List[Dict[str, str]]] = {}
_USER_HISTORY_LIMIT = 50

logger = logging.getLogger(__name__)

@dataclass
class SessionState:
    role: str  # "REQUESTER" | "AGENT" | "ADMIN"
    user_id: int
    active_ticket_id: Optional[int] = None
    history: List[Dict[str, str]] = field(default_factory=list)  # [{"role": "user|assistant", "content": "..."}]
    last_intent: Optional[str] = None


def _extract_ticket_id_from_text(text: str) -> Optional[int]:
    m = re.search(r"#(\d+)", text)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _is_confirmation(text: str) -> bool:
    t = text.strip().lower()
    return t in {
        "yes",
        "yeah",
        "yep",
        "ok",
        "okay",
        "sure",
        "please do",
        "do it",
        "confirm",
    } or t.startswith(("yes ", "yeah ", "yep ", "ok ", "okay ", "sure "))


def _format_history_snippet(history: List[Dict[str, str]], max_items: int = 4) -> str:
    recent = history[-max_items:]
    lines = []
    for m in recent:
        role = m.get("role", "?")
        content = m.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _last_assistant_message(state: "SessionState") -> Optional[Dict[str, str]]:
    return next((m for m in reversed(state.history) if m.get("role") == "assistant"), None)


def _last_user_message(state: "SessionState") -> Optional[str]:
    msg = next((m for m in reversed(state.history) if m.get("role") == "user"), None)
    return msg.get("content") if msg else None


def _last_user_message_global(user_id: int) -> Optional[str]:
    hist = _USER_HISTORY.get(user_id, [])
    for m in reversed(hist):
        if m.get("role") == "user":
            return m.get("content")
    return None


def _append_history(user_id: int, role: str, content: str) -> None:
    hist = _USER_HISTORY.setdefault(user_id, [])
    hist.append({"role": role, "content": content})
    # Cap history length
    if len(hist) > _USER_HISTORY_LIMIT:
        del hist[0 : len(hist) - _USER_HISTORY_LIMIT]


def _sanitize_msg(msg: str, limit: int = 500) -> str:
    clean = (msg or "").replace("\n", " ").strip()
    if len(clean) > limit:
        clean = clean[: limit - 3] + "..."
    return clean


def _role_allows_intent(role: str, intent: str) -> bool:
    if intent in {"create_ticket", "check_status", "add_info"}:
        return True
    if intent == "agent_triage_help":
        return role in {"AGENT", "ADMIN"}
    if intent == "admin_metrics":
        return role == "ADMIN"
    # small_talk or unknown fallback is fine
    return True


async def _is_help_or_capabilities_question(user_message: str) -> bool:
    """
    Use LLM to intelligently detect if the user is asking about their capabilities,
    what they can do, or how to use the system.
    """
    system_prompt = (
        "You are a classifier for an IT helpdesk chatbot.\n"
        "Determine if the user is asking about:\n"
        "- Their capabilities or permissions\n"
        "- What they can do with the system\n"
        "- How to use the tool\n"
        "- What features are available to them\n"
        "- Help or documentation about their access\n\n"
        "Respond with ONLY 'yes' if it's a help/capabilities question, or 'no' otherwise.\n"
        "Examples of YES: 'what can I do?', 'show me my permissions', 'how do I use this?', 'what am I allowed to do?', 'help me understand my access'\n"
        "Examples of NO: 'create a ticket', 'what's the status?', 'hello', 'thanks'"
    )
    
    try:
        response = llm_complete(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            model="gpt-4o-mini",
            temperature=0.1,
            max_tokens=10,
        )
        result = (response.get("content", "") or "").strip().lower()
        return result.startswith("yes")
    except Exception as e:
        logger.warning(f"Error detecting help question, falling back to keyword matching: {e}")
        # Fallback to keyword matching if LLM fails
        lower_msg = user_message.lower()
        help_keywords = [
            "what can", "capabilities", "permissions", "access", "features",
            "help me understand", "how do i", "what am i", "show me my",
            "what are my", "what can this", "how to use", "manual", "guide"
        ]
        return any(keyword in lower_msg for keyword in help_keywords)


async def _run_agent(agent, prompt: str) -> str:
    result = await Runner.run(agent, prompt)
    if result.final_output:
        return result.final_output

    for item in reversed(result.new_items):
        if isinstance(item, MessageOutputItem):
            txt = ItemHelpers.text_message_output(item)
            if txt:
                return txt

    return "I couldn't generate a response for that request."


async def orchestrate_turn(
    user_message: str,
    state: SessionState,
) -> Tuple[str, SessionState]:
    """
    Main entrypoint for a single chat turn.

    Parameters:
    - user_message: raw message from chat UI.
    - state: current SessionState (mutable copy will be returned).
    """
    # 1) Route intent
    routing = await run_router(
        user_message=user_message,
        role=state.role,
        active_ticket_id=state.active_ticket_id,
    )
    intent = routing.get("intent", "small_talk")
    ticket_hint = routing.get("ticket_hint")

    logger.info(
        "route_decision",
        extra={
            "user_id": state.user_id,
            "role": state.role,
            "intent": intent,
            "ticket_hint": ticket_hint,
            "user_msg": _sanitize_msg(user_message),
        },
    )

    # If router surfaced a ticket id, treat it as the active ticket for this turn
    if ticket_hint:
        state.active_ticket_id = ticket_hint

    # If user is asking to assign/reassign, force triage intent
    lower_msg = user_message.lower()
    if "assign" in lower_msg or "reassign" in lower_msg:
        intent = "agent_triage_help"

    # Override intent on explicit confirmation following an Intake or Triage prompt
    last_assistant = _last_assistant_message(state)
    if _is_confirmation(user_message) and last_assistant:
        last_content = (last_assistant.get("content") or "").lower()
        if "create this ticket" in last_content or "should i create" in last_content or "create a ticket" in last_content:
            intent = "create_ticket"
        if "assign this ticket" in last_content or "assign ticket" in last_content or "proceed to assign" in last_content:
            intent = "agent_triage_help"

    # If we were in create_ticket or agent_triage_help last turn and the router fell back, keep flow
    if state.last_intent in {"create_ticket", "agent_triage_help"} and intent in {"small_talk", "add_info"}:
        intent = state.last_intent

    # 2) Enforce role-based permissions on intent
    if not _role_allows_intent(state.role, intent):
        reply = (
            f"As {state.role}, you are not allowed to perform '{intent}'. "
            "Please adjust your request or switch to a permitted role."
        )
        logger.warning(
            "intent_denied",
            extra={"user_id": state.user_id, "role": state.role, "intent": intent},
        )
        state.history.append({"role": "user", "content": user_message})
        state.history.append({"role": "assistant", "content": reply})
        return reply, state

    # 3) Choose agent / path based on intent and role
    agent = None
    context_lines: List[str] = [
        f"User role: {state.role}",
        f"User id: {state.user_id}",
        f"Active ticket id: {state.active_ticket_id or 'none'}",
        f"Router intent: {intent}",
    ]

    if intent == "create_ticket":
        agent = intake_agent
        from services.cache import get_categories

        cats = get_categories()
        cat_line = "Available categories (id:name): " + ", ".join(f"{c['id']}:{c['name']}" for c in cats)
        context_lines.append("You are onboarding a NEW issue and should end by creating a ticket when the user confirms.")
        context_lines.append(cat_line)
        context_lines.append(f"Requester id to use when calling tools: {state.user_id}")
    elif intent in ("check_status", "add_info"):
        # Requester/Agent/Admin asking about or updating an existing ticket
        agent = status_agent
        context_lines.append(
            "You are handling ticket status/updates. Use active_ticket_id when the user does not specify one explicitly."
        )
    elif intent == "agent_triage_help":
        # Agent asking to triage an existing ticket
        agent = triage_agent
        context_lines.append(
            "You are helping an AGENT triage an existing ticket (category/priority/assignee)."
        )
    elif intent in ("list_tickets", "admin_metrics"):
        # Admin/agent asking for lists/metrics
        agent = ops_analytics_agent
        context_lines.append(
            "You are answering an admin/ops style query about ticket queues, volumes, or metrics."
        )
    else:
        # Small talk or unknown: respond with a helpful fallback
        lower_msg = user_message.lower()
        if "last query" in lower_msg or "last question" in lower_msg or "what did i ask" in lower_msg:
            last_user = _last_user_message_global(state.user_id) or _last_user_message(state)
            if last_user:
                reply = f"Your last query was: {last_user}"
            else:
                reply = "I don't have an earlier message from you."
        else:
            # Intelligently detect if this is a help/capabilities question using LLM
            is_help_question = await _is_help_or_capabilities_question(user_message)
            
            if is_help_question:
                # Provide role-specific help manual
                if state.role == "REQUESTER":
                    reply = (
                        "As a **Requester**, you can:\n\n"
                        "1. **Create new tickets** - Describe an issue (e.g., 'I can't connect to WiFi') and I'll help you create a ticket.\n"
                        "2. **Check ticket status** - Ask 'What's the status of my ticket?' or 'Show me ticket #123'.\n"
                        "3. **Add information** - Provide updates to existing tickets with more details or attachments.\n"
                        "4. **Close/Reopen tickets** - Close your RESOLVED tickets or reopen CLOSED ones if needed.\n\n"
                        "Try: 'I need help with VPN' or 'What's the status of my last ticket?'"
                    )
                elif state.role == "AGENT":
                    reply = (
                        "As an **Agent**, you can do everything a Requester can, plus:\n\n"
                        "1. **Triage tickets** - Ask 'Help me triage ticket #123' or 'Assign ticket #10 to the Network Team'.\n"
                        "2. **Update ticket status** - Move tickets through: NEW → TRIAGED → IN_PROGRESS → RESOLVED.\n"
                        "3. **Add internal notes** - Comments visible only to agents/admins.\n"
                        "4. **Update priority and assignee** - Change priority levels and assign tickets to team members.\n"
                        "5. **View ticket lists** - Ask 'Show me all P1 tickets' or 'What tickets are assigned to me?'\n\n"
                        "Try: 'Help me triage ticket #5' or 'Show me all NEW tickets'"
                    )
                elif state.role == "ADMIN":
                    reply = (
                        "As an **Admin**, you have full access:\n\n"
                        "1. **Everything Agents can do** - All ticket management, triage, and updates.\n"
                        "2. **View analytics and metrics** - Ask 'How many P1 tickets are open?' or 'Show tickets by category'.\n"
                        "3. **Override any status** - Bypass normal status transition rules when needed.\n"
                        "4. **Full system access** - View all tickets, metrics, and system data.\n\n"
                        "Try: 'Show me ticket metrics' or 'How many tickets are in each status?'"
                    )
                else:
                    reply = (
                        "I'm your IT helpdesk assistant. "
                        "You can describe a new issue, ask about a ticket's status, "
                        "or, if you're an agent/admin, ask for triage help or metrics."
                    )
            else:
                reply = (
                    "I'm your IT helpdesk assistant. "
                    "You can describe a new issue, ask about a ticket's status, "
                    "or, if you're an agent/admin, ask for triage help or metrics."
                )
        state.history.append({"role": "user", "content": user_message})
        state.history.append({"role": "assistant", "content": reply})
        return reply, state

    # Safety: if we somehow ended up without an agent
    if agent is None:
        reply = "I wasn't able to determine which helper should respond to that. Please rephrase your request."
        state.history.append({"role": "user", "content": user_message})
        state.history.append({"role": "assistant", "content": reply})
        return reply, state

    # Build agent prompt with inline context
    context_block = "\n".join(context_lines)
    history_snippet = _format_history_snippet(state.history, max_items=4)
    agent_input = f"{context_block}\n\nRecent conversation:\n{history_snippet}\n\nUser message: {user_message}"

    try:
        assistant_reply = await _run_agent(agent, agent_input)
    except Exception as e:
        logger.error(
            "agent_run_failed",
            extra={"user_id": state.user_id, "role": state.role, "intent": intent, "error": str(e)},
        )
        assistant_reply = (
            "I hit a system error while handling that request. Please try again in a moment or rephrase."
        )

    # Post-processing & state update
    state.history.append({"role": "user", "content": user_message})
    state.history.append({"role": "assistant", "content": assistant_reply})
    _append_history(state.user_id, "user", user_message)
    _append_history(state.user_id, "assistant", assistant_reply)
    state.last_intent = intent

    # Try to capture ticket id from assistant reply to set active_ticket_id
    new_id = _extract_ticket_id_from_text(assistant_reply)
    if new_id:
        state.active_ticket_id = new_id

    return assistant_reply, state


__all__ = ["SessionState", "orchestrate_turn"]


