"""
Streamlit chat UI for the multi-agent IT helpdesk chatbot.

Features (from requirements):
- Role selector (Requester / Agent / Admin) in sidebar.
- User switcher dropdown based on seeded users.
- Chat-style interface that calls the orchestrator per message.
- Small ticket context panel showing the active ticket (if any).
"""

from __future__ import annotations

import os
import asyncio
from pathlib import Path

import streamlit as st

from services.orchestrator import SessionState, orchestrate_turn
from services.user_service import list_users
from services.cache import get_categories
from services.ticket_service import add_attachment, list_attachments


ROLE_LABEL_TO_INTERNAL = {
    "Requester": "REQUESTER",
    "Agent": "AGENT",
    "Admin": "ADMIN",
}

INTERNAL_TO_ROLE_LABEL = {v: k for k, v in ROLE_LABEL_TO_INTERNAL.items()}


def _ensure_session_state(selected_role: str, selected_user_id: int) -> None:
    """
    Initialize or update the orchestrator SessionState stored in Streamlit's session_state.
    Resets conversation state when the user changes.
    """
    internal_role = ROLE_LABEL_TO_INTERNAL[selected_role]

    # If no session_state yet, create one
    if "session_state" not in st.session_state:
        st.session_state.session_state = SessionState(
            role=internal_role,
            user_id=selected_user_id,
        )
        return

    ss: SessionState = st.session_state.session_state

    # If the selected user changed, reset conversation state
    if ss.user_id != selected_user_id:
        st.session_state.session_state = SessionState(
            role=internal_role,
            user_id=selected_user_id,
        )
        return

    # Otherwise just update role/user
    ss.role = internal_role
    ss.user_id = selected_user_id


def main() -> None:
    st.set_page_config(page_title="IT Helpdesk Chatbot", layout="wide")
    st.title("IT Helpdesk Ticketing Chatbot")

    # Sidebar: role + user selector
    with st.sidebar:
        st.header("Session")
        role_label = st.selectbox("Role", list(ROLE_LABEL_TO_INTERNAL.keys()), index=0)

        # Show users; optionally filter by role when Requester so demo is clearer.
        filter_role = None
        if role_label == "Requester":
            filter_role = "REQUESTER"
        users = list_users(role=filter_role)
        if not users:
            st.error("No users found in the database. Run seed_data.py first.")
            return

        user_labels = [f"{u['id']}: {u['name']} ({u['role']})" for u in users]
        default_index = 0
        selected_label = st.selectbox("User", user_labels, index=default_index)
        selected_user = users[user_labels.index(selected_label)]

        _ensure_session_state(role_label, selected_user["id"])

        # Optional context: categories overview for demo/debug
        with st.expander("Reference: Categories", expanded=False):
            for c in get_categories():
                st.write(f"- {c['id']}: {c['name']} (default {c['default_priority']})")

    ss: SessionState = st.session_state.session_state

    # Ticket context panel + attachments
    with st.sidebar:
        st.markdown("---")
        st.subheader("Active Ticket")
        if ss.active_ticket_id:
            st.write(f"Currently focused on ticket **#{ss.active_ticket_id}**.")
            st.caption(
                "Ask: 'What is the status of my ticket?' or 'Add a comment to my ticket' "
                "to interact with this ticket."
            )

            st.markdown("**Attachments**")
            uploaded = st.file_uploader("📎 Attach file to this ticket", type=None, key="attach_uploader")
            if uploaded is not None:
                uploads_dir = Path("uploads")
                uploads_dir.mkdir(parents=True, exist_ok=True)
                filename = Path(uploaded.name).name
                file_bytes = uploaded.getvalue()
                save_path = uploads_dir / filename
                with open(save_path, "wb") as f:
                    f.write(file_bytes)
                try:
                    add_attachment(
                        ss.active_ticket_id,
                        {
                            "filename": filename,
                            "url": str(save_path),
                            "size_bytes": len(file_bytes),
                            "actor_id": ss.user_id,
                        },
                    )
                    st.success(f"Attached {filename} ({len(file_bytes)} bytes) to ticket #{ss.active_ticket_id}")
                except Exception as e:
                    st.error(f"Failed to attach file: {e}")

            # Show existing attachments
            try:
                attachments = list_attachments(ss.active_ticket_id)
                if attachments:
                    for att in attachments:
                        st.write(f"- {att['file_name']} ({att['size_bytes']} bytes) @ {att['uploaded_at']}")
                else:
                    st.caption("No attachments yet.")
            except Exception:
                st.caption("Attachments unavailable right now.")
        else:
            st.write("No active ticket yet. Describe an issue to create one.")

    # Chat history display using SessionState.history
    chat_container = st.container()
    with chat_container:
        for msg in ss.history:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Describe your IT issue or ask about a ticket..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Call orchestrator (async -> sync)
        reply, new_state = asyncio.run(orchestrate_turn(prompt, ss))
        st.session_state.session_state = new_state

        with st.chat_message("assistant"):
            st.markdown(reply)


if __name__ == "__main__":
    main()


