"""
Simple user service helpers for the Streamlit UI and orchestrator.

These functions provide read-only access to users so the UI can offer
role-based user selection without duplicating SQL everywhere.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from psycopg2 import extras

from database.connection import get_db_connection


def list_users(role: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Return all users (optionally filtered by role).
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        if role:
            cursor.execute(
                "SELECT id, name, email, role, team_id FROM users WHERE role = %s ORDER BY id;",
                (role,),
            )
        else:
            cursor.execute(
                "SELECT id, name, email, role, team_id FROM users ORDER BY id;",
            )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


__all__ = ["list_users"]


