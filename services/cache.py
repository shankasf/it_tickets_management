"""
Lightweight in-memory caching for reference data that is read frequently
but changes rarely (teams, categories, SLA policies).

This is intentionally simple and process-local, suitable for the demo
scale described in the requirements (≈100 active users/minute).
"""

from __future__ import annotations

from typing import Any, Dict, List

from psycopg2 import extras

from database.connection import get_db_connection


_teams_cache: List[Dict[str, Any]] | None = None
_categories_cache: List[Dict[str, Any]] | None = None
_sla_policies_cache: List[Dict[str, Any]] | None = None


def get_teams() -> List[Dict[str, Any]]:
    global _teams_cache
    if _teams_cache is not None:
        return _teams_cache

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute("SELECT id, name FROM teams ORDER BY id;")
        rows = cursor.fetchall()
        _teams_cache = [dict(row) for row in rows]
        return _teams_cache
    finally:
        conn.close()


def get_categories() -> List[Dict[str, Any]]:
    global _categories_cache
    if _categories_cache is not None:
        return _categories_cache

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute("SELECT id, name, default_priority FROM categories ORDER BY id;")
        rows = cursor.fetchall()
        _categories_cache = [dict(row) for row in rows]
        return _categories_cache
    finally:
        conn.close()


def get_sla_policies() -> List[Dict[str, Any]]:
    global _sla_policies_cache
    if _sla_policies_cache is not None:
        return _sla_policies_cache

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            "SELECT id, name, priority, first_response_minutes, resolution_minutes "
            "FROM sla_policies ORDER BY id;"
        )
        rows = cursor.fetchall()
        _sla_policies_cache = [dict(row) for row in rows]
        return _sla_policies_cache
    finally:
        conn.close()


__all__ = ["get_teams", "get_categories", "get_sla_policies"]


