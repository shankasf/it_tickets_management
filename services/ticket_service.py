import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import psycopg2
from psycopg2 import extras

from database.connection import get_db_connection

logger = logging.getLogger(__name__)

# Constants
VALID_STATUS = {
    "NEW",
    "TRIAGED",
    "IN_PROGRESS",
    "WAITING_ON_REQUESTER",
    "WAITING_ON_VENDOR",
    "RESOLVED",
    "CLOSED",
    "REOPENED",
}

VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}
VALID_ROLES = {"REQUESTER", "AGENT", "ADMIN"}

def is_allowed_transition(current_status: str, new_status: str, user_role: str) -> bool:
    if user_role == "ADMIN":
        return True
    if user_role == "REQUESTER":
        return (current_status, new_status) in {
            ("RESOLVED", "CLOSED"),
            ("CLOSED", "REOPENED"),
        }
    
    if user_role == "AGENT":
        allowed = {
            ("NEW", "TRIAGED"),
            ("TRIAGED", "IN_PROGRESS"),
            ("IN_PROGRESS", "RESOLVED"),
            ("IN_PROGRESS", "WAITING_ON_REQUESTER"),
            ("IN_PROGRESS", "WAITING_ON_VENDOR"),
            ("WAITING_ON_REQUESTER", "IN_PROGRESS"),
            ("WAITING_ON_VENDOR", "IN_PROGRESS"),
            ("TRIAGED", "WAITING_ON_REQUESTER"),
            ("TRIAGED", "WAITING_ON_VENDOR"),
        }

        return (current_status, new_status) in allowed
    return False


def _validate_fk(cursor, table: str, row_id: int) -> bool:
    cursor.execute(f"SELECT 1 FROM {table} WHERE id = %s", (row_id,))
    return cursor.fetchone() is not None

# ===================================================================================
#                               Create Ticket
# ===================================================================================
def create_ticket(payload: Dict[str, Any]) -> Dict[str, Any]:
    required = ["title", "description", "category_id", "priority", "requester_id"]
    
    for key in required:
        if not payload.get(key):
            raise ValueError(f"Missing required field: {key}")
    
    if payload["priority"] not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: {payload['priority']}")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Validate the FK references
        for fk_table, fk_key in [
            ("categories", "category_id"),
            ("users", "requester_id"),
        ]:
            if not _validate_fk(cursor, fk_table, payload[fk_key]):
                raise ValueError(f"Invalid {fk_table} Id not found: {payload[fk_key]}")
        
        if payload.get("assignee_id") and not _validate_fk(cursor, "users", payload["assignee_id"]):
            raise ValueError(f"Invalid assignee Id not found: {payload['assignee_id']}")
        
        sla_policy_id = payload.get("sla_policy_id")
        resolution_minutes = None
        if sla_policy_id:
            cursor.execute(
                "SELECT resolution_minutes FROM sla_policies WHERE id = %s",
                (sla_policy_id,),
            )

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Invalid SLA policy Id not found: {sla_policy_id}")
            resolution_minutes = row[0]
    
        created_at = datetime.now()
        due_at = (
            created_at + timedelta(minutes=resolution_minutes)
            if resolution_minutes is not None
            else None
        )

        cursor.execute(
            """
            INSERT INTO tickets
            (title, description, status, priority, category_id, requester_id, assignee_id, sla_policy_id, created_at, due_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                payload["title"],
                payload["description"],
                payload.get("status", "NEW"),
                payload["priority"],
                payload["category_id"],
                payload["requester_id"],
                payload.get("assignee_id"),
                sla_policy_id,
                created_at,
                due_at,
            ),
        )

        ticket = cursor.fetchone()

        # Initial comment
        if payload.get("initial_comment"):
            cursor.execute(
                """
                INSERT INTO comments (ticket_id, author_id, body, is_internal)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    ticket["id"],
                    payload["requester_id"],
                    payload["initial_comment"],
                    False,
                ),
            )

        # Audit event for ticket creation
        cursor.execute(
            """
            INSERT INTO audit_events (ticket_id, actor_id, action, meta)
            VALUES (%s, %s, %s, %s);
            """,
            (
                ticket["id"],
                payload["requester_id"],
                "TICKET_CREATED",
                extras.Json({"title": payload["title"], "priority": payload["priority"]}),
            ),
        )

        conn.commit()
        return dict(ticket)
    
    except psycopg2.Error as e:
        logger.error(f"Error creating ticket: {e}")
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating ticket: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# ===================================================================================
#                               Update Ticket
# ===================================================================================

def update_ticket(ticket_id: int, patch: Dict[str, Any], actor_role: str, actor_id: int) -> Dict[str, Any]:
    if actor_role not in VALID_ROLES:
        raise ValueError(f"Invalid actor role: {actor_role}")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        cursor.execute(
            "SELECT * FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        existing = cursor.fetchone()
        if not existing:
            raise ValueError(f"Ticket not found")
        
        #validate status transistion
        if "status" in patch:
            new_status = patch["status"]
            if new_status not in VALID_STATUS:
                raise ValueError(f"Invalid status: {new_status}")
            if not is_allowed_transition(existing["status"], new_status, actor_role):
                raise ValueError(f"Status transition not allowed: {existing['status']} -> {new_status}")
        
        #validate priority
        if "priority" in patch and patch["priority"] not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {patch['priority']}")
        
        # Validate assignee
        if "assignee_id" in patch and patch["assignee_id"] is not None:
            if not _validate_fk(cursor, "users", patch["assignee_id"]):
                raise ValueError(f"Invalid assignee Id not found")
        
        #validate SLA policy
        sla_policy_id = patch.get("sla_policy_id")
        resolution_minutes = None
        if "sla_policy_id" in patch:
            if sla_policy_id is not None:
                cursor.execute(
                    "SELECT resolution_minutes FROM sla_policies WHERE id = %s",
                    (sla_policy_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Invalid SLA policy Id not found")
                resolution_minutes = row[0]
        
        # Build the dynamic update query
        fields = []
        values = []
        for key in ["title", "description", "priority", "category_id", "assignee_id", "sla_policy_id"]:
            if key in patch:
                fields.append(f"{key} = %s")
                values.append(patch[key])
        
        # We will recompute the due_at if the SLA policy changes
        if resolution_minutes is not None:
            due_at = datetime.now() + timedelta(minutes=resolution_minutes)
            fields.append("due_at = %s")
            values.append(due_at)
        
        if not fields:
            return dict(existing) # there is nothing to update
        
        #updated at
        fields.append("updated_at = NOW()")

        values.append(ticket_id)
        cursor.execute(
            f"UPDATE tickets SET {', '.join(fields)} WHERE id = %s RETURNING *;",
            tuple(values),
        )

        updated = cursor.fetchone()

        # Audit events
        if "status" in patch:
            cursor.execute(
                """
                INSERT INTO audit_events (ticket_id, actor_id, action, meta)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    ticket_id,
                    actor_id,
                    "TICKET_STATUS_UPDATED",
                    extras.Json({"before": existing["status"], "after": patch["status"]}),
                ),
            )

        if "assignee_id" in patch:
            cursor.execute("""
            INSERT INTO audit_events (ticket_id, actor_id, action, meta)
            VALUES (%s, %s, %s, %s);
            """,
            (
                ticket_id,
                actor_id,
                "TICKET_ASSIGNEE_UPDATED",
                extras.Json({"before": existing["assignee_id"], "after": patch["assignee_id"]}),
            ),
            )
        
        if "priority" in patch:
            cursor.execute(
                """
                INSERT INTO audit_events (ticket_id, actor_id, action, meta)
                VALUES (%s, %s, %s, %s);
                """,
                (
                    ticket_id,
                    actor_id,
                    "TICKET_PRIORITY_UPDATED",
                    extras.Json({"before": existing["priority"], "after": patch["priority"]}),
                ),
            )
        
        conn.commit()
        return dict(updated)
    except psycopg2.Error as e:
        logger.error(f"Error updating ticket: {e}")
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating ticket: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

# ===================================================================================
#                               ADD COMMENT
# ===================================================================================

def add_comment(ticket_id: int, comment_payload: Dict[str, Any]) -> Dict[str, Any]:
    required = ["author_id", "body"]
    for key in required:
        if not comment_payload.get(key):
            raise ValueError(f"Missing required field: {key}")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        #Ensure the ticket exists
        cursor.execute(
            "SELECT 1 FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        if not cursor.fetchone():
            raise ValueError(f"Ticket not found")
        
        is_internal = bool(comment_payload.get("is_internal", False))
        cursor.execute(
            """
            INSERT INTO comments (ticket_id, author_id, body, is_internal, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING *;
            """,
            (
                ticket_id,
                comment_payload["author_id"],
                comment_payload["body"],
                is_internal,
            ),
        )

        comment = cursor.fetchone()

        #Audit event
        cursor.execute(
            """
            INSERT INTO audit_events (ticket_id, actor_id, action, meta)
            VALUES (%s, %s, %s, %s);
            """,
            (
                ticket_id,
                comment_payload["author_id"],
                "COMMENT_ADDED",
                extras.Json({"is_internal": is_internal}),
            ),
        )

        conn.commit()
        return dict(comment)
    except psycopg2.Error as e:
        logger.error(f"Error adding comment: {e}")
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding comment: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# ===================================================================================
#                               list tickets
# ===================================================================================

def list_tickets(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:

    filters = filters or {}
    clauses = []
    params = []

    # Normalize common enum filters to uppercase to avoid invalid enum errors
    norm_status = filters.get("status")
    if norm_status:
        filters["status"] = str(norm_status).upper()
    norm_priority = filters.get("priority")
    if norm_priority:
        filters["priority"] = str(norm_priority).upper()

    for key in ["status", "priority", "assignee_id", "requester_id", "category_id"]:
        if key in filters:
            clauses.append(f"{key} = %s")
            params.append(filters[key])
    
    #Date range
    if filters.get("created_after"):
        clauses.append("created_at >= %s")
        params.append(filters["created_after"])
    
    if filters.get("created_before"):
        clauses.append("created_at <= %s")
        params.append(filters["created_before"])
    
    # Search in title/description
    if filters.get("search"):
        clauses.append("(title ILIKE %s OR description ILIKE %s)")
        term = f"%{filters['search']}%"
        params.extend([term, term])
    
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order_sql = "ORDER BY created_at DESC"
    limit_sql = ""
    if "limit" in filters:
        limit_sql += " LIMIT %s"
        params.append(filters["limit"])
    if "offset" in filters:
        limit_sql += " OFFSET %s"
        params.append(filters["offset"])
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(f"SELECT * FROM tickets {where_sql} {order_sql} {limit_sql};", tuple(params))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except psycopg2.Error as e:
        logger.error(f"Error listing tickets: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing tickets: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")

# ===================================================================================
#                               get ticket by id
# ===================================================================================

def get_ticket(ticket_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except psycopg2.Error as e:
        logger.error(f"Error getting ticket: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting ticket: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# ===================================================================================
#                               get ticket with comments
# ===================================================================================

def get_ticket_with_comments(ticket_id: int, user_role: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM tickets WHERE id = %s",
            (ticket_id,),
        )
        ticket = cursor.fetchone()
        if not ticket:
            return None
        
        include_internal = user_role in ("AGENT", "ADMIN")
        if include_internal:
            cursor.execute(
                "SELECT * FROM comments WHERE ticket_id = %s ORDER BY created_at ASC;",
                (ticket_id,),
            )
        else:
            cursor.execute(
                "SELECT * FROM comments WHERE ticket_id = %s AND is_internal = false ORDER BY created_at ASC;",
                (ticket_id,),
            )
        
        comments = cursor.fetchall()
        result = dict(ticket)
        result["comments"] = [dict(comment) for comment in comments]
        return result
    except psycopg2.Error as e:
        logger.error(f"Error getting ticket with comments: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting ticket with comments: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# ===================================================================================
#                               get metrics
# ===================================================================================

def get_metrics(filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    filters = filters or {}
    clauses = []
    params = []

    if filters.get("created_after"):
        clauses.append("created_at >= %s")
        params.append(filters["created_after"])
    if filters.get("created_before"):
        clauses.append("created_at <= %s")
        params.append(filters["created_before"])
    
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # By status
        cursor.execute(
            f"SELECT status, COUNT(*) AS count FROM tickets {where_sql} GROUP BY status;",
            tuple(params),
        )
        by_status = cursor.fetchall()

        # By priority
        cursor.execute(
            f"SELECT priority, COUNT(*) AS count FROM tickets {where_sql} GROUP BY priority;",
            tuple(params),
        )
        by_priority = cursor.fetchall()

        # BY Category
        cursor.execute(
            f"""
            SELECT c.name, COUNT(*) AS count FROM tickets t
            JOIN categories c ON t.category_id = c.id
            {where_sql} GROUP BY c.name;
            """,
            tuple(params),
        )
        by_category = cursor.fetchall()

        return {
            "by_status": [dict(row) for row in by_status],
            "by_priority": [dict(row) for row in by_priority],
            "by_category": [dict(row) for row in by_category],
        }
    except psycopg2.Error as e:
        logger.error(f"Error getting metrics: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting metrics: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


# ===================================================================================
#                               attachments
# ===================================================================================

def add_attachment(ticket_id: int, attachment: Dict[str, Any]) -> Dict[str, Any]:
    required = ["filename", "url", "size_bytes", "actor_id"]
    for key in required:
        if attachment.get(key) in (None, ""):
            raise ValueError(f"Missing required field: {key}")

    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Ensure the ticket exists
        cursor.execute("SELECT 1 FROM tickets WHERE id = %s", (ticket_id,))
        if not cursor.fetchone():
            raise ValueError("Ticket not found")

        cursor.execute(
            """
            INSERT INTO attachments (ticket_id, file_name, url, size_bytes, uploaded_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING *;
            """,
            (
                ticket_id,
                attachment["filename"],
                attachment["url"],
                attachment["size_bytes"],
            ),
        )

        row = cursor.fetchone()

        # Audit event
        cursor.execute(
            """
            INSERT INTO audit_events (ticket_id, actor_id, action, meta)
            VALUES (%s, %s, %s, %s);
            """,
            (
                ticket_id,
                attachment["actor_id"],
                "ATTACHMENT_ADDED",
                extras.Json(
                    {
                        "filename": attachment["filename"],
                        "size_bytes": attachment["size_bytes"],
                    }
                ),
            ),
        )

        conn.commit()
        return dict(row)
    except psycopg2.Error as e:
        logger.error(f"Error adding attachment: {e}")
        conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding attachment: {e}")
        conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")


def list_attachments(ticket_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(
            """
            SELECT id, ticket_id, file_name, url, size_bytes, uploaded_at
            FROM attachments
            WHERE ticket_id = %s
            ORDER BY uploaded_at ASC;
            """,
            (ticket_id,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except psycopg2.Error as e:
        logger.error(f"Error listing attachments: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error listing attachments: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")
