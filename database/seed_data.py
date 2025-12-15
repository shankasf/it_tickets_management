from connection import get_db_connection
import psycopg2
from psycopg2 import extras
from datetime import datetime, timedelta
import random
import logging

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_existing_data(connection):
    """ It will clear all existing data from the database """
    cursor = connection.cursor()

    try:
        logger.info("Clearing existing data...")

        cursor.execute("DELETE FROM audit_events;")
        cursor.execute("DELETE FROM attachments;")
        cursor.execute("DELETE FROM comments;")
        cursor.execute("DELETE FROM tickets;")
        cursor.execute("DELETE FROM sla_policies;")
        cursor.execute("DELETE FROM categories;")
        cursor.execute("DELETE FROM users;")
        cursor.execute("DELETE FROM teams;")
        connection.commit()
        logger.info("Existing data cleared successfully")
    except psycopg2.Error as e:
        logger.error(f"Error clearing existing data: {e}")
        connection.rollback()
        raise

def seed_teams(connection):
    """ This function populates 3-5 teams"""
    cursor = connection.cursor()
    teams_data = [
        "Service Desk",
        "Network Team",
        "Security Team",
        "Hardware Support",
        "Software Support"
    ]

    teams_dict = {}

    try:
        logger.info("Seeding teams...")
        for team_name in teams_data:
            cursor.execute("SELECT id FROM teams WHERE name = %s", (team_name,))
            existing = cursor.fetchone()
            if existing:
                teams_dict[team_name] = existing[0]
                logger.info(f"Team {team_name} already exists with ID {existing[0]}")
            else:
                cursor.execute("INSERT INTO teams (name) VALUES (%s) RETURNING id", (team_name,))
                team_id = cursor.fetchone()[0]
                teams_dict[team_name] = team_id
                logger.info(f"Team {team_name} seeded successfully with ID {team_id}")
        connection.commit()
        logger.info(f"Successfully seeded {len(teams_dict)} teams")
        return teams_dict
        
    except psycopg2.Error as e:
        logger.error(f"Error seeding teams: {e}")
        connection.rollback()
        raise

def seed_users(connection, teams_dict):
    """ Inserting 10-20 users (mix of Requesters, Agents, Admins) """
    cursor = connection.cursor()

    users_data = [
        # Requesters
        ("Sarath Kumar", "sarath@example.com", "REQUESTER", None),
        ("Ashish Thange", "ashish@example.com", "REQUESTER", None),
        ("Sai Kiran", "sai@example.com", "REQUESTER", None),
        ("Sai Pranith", "pranith@example.com", "REQUESTER", None),
        ("Giri Teja", "giri@example.com", "REQUESTER", None),
        ("Barth Kumar", "barth@example.com", "REQUESTER", None),
        ("Sai Teja", "teja@example.com", "REQUESTER", None),
        ("Jahnavi", "jahnavi@example.com", "REQUESTER", None),
        ("Bargavi", "bargavi@example.com", "REQUESTER", None),
        ("Sushma", "sushma@example.com", "REQUESTER", None),
        ("Rajesh", "rajesh@example.com", "REQUESTER", None),
        ("Dilip", "dilip@example.com", "REQUESTER", None),

        # Agents
        ("ramya", "ramya@example.com", "AGENT", "Service Desk"),
        ("suresh", "suresh@example.com", "AGENT", "Network Team"),
        ("kumar", "kumar@example.com", "AGENT", "Security Team"),
        ("kiran", "kiran@example.com", "AGENT", "Hardware Support"),
        ("Alex Chen", "alex@example.com", "AGENT", "Software Support"),
        ("John Doe", "john@example.com", "AGENT", "Service Desk"),

        # Admins
        ("Sunil Gundala", "sunil@example.com", "ADMIN", None),
        ("Harsha Vardhan", "harsha@example.com", "ADMIN", None),
    ]

    user_dict = {
        "REQUESTER": [],
        "AGENT": [],
        "ADMIN": [],
    }

    try:
        logger.info("Seeding users...")
        for name, email, role, team_name in users_data:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing = cursor.fetchone()

            if existing:
                user_id = existing[0]
                logger.info(f"User {name} already exists with ID {user_id}")
            else:
                team_id = teams_dict.get(team_name) if team_name else None
                cursor.execute("INSERT INTO users (name, email, role, team_id) VALUES (%s, %s, %s, %s) RETURNING id", (name, email, role, team_id))
                user_id = cursor.fetchone()[0]
                logger.info(f"User {name} created successfully with ID {user_id}")
        
            user_dict[role].append(user_id)
        
        connection.commit()
        logger.info(f"Successfully created {len(user_dict)} users")
        return user_dict
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding users: {e}")
        connection.rollback()
        raise

def seed_categories(connection=None):
    """ Inserting 6-10 categories with sla polices """
    cursor = connection.cursor()

    categories_data = [
        ("Access Request", "P3"),
        ("Network Issue", "P2"),
        ("Hardware Problem", "P2"),
        ("Software Issue", "P1"),
        ("Security Incident", "P1"),
        ("Email Issue", "P4"),
        ("VPN Issue", "P3"),
        ("Printer Issue", "P4"),
        ("Password Reset", "P4"),
        ("Application Access", "P3"),
    ]

    categories_dict = {}

    try:
        logger.info("Seeding categories...")
        for name, default_priority in categories_data:
            cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
            existing = cursor.fetchone()

            if existing:
                categories_dict[name] = existing[0]
                logger.info(f"Category {name} already exists with ID {existing[0]}")
            else:
                cursor.execute("INSERT INTO categories (name, default_priority) VALUES (%s, %s) RETURNING id", (name, default_priority))
                category_id = cursor.fetchone()[0]
                categories_dict[name] = category_id
                logger.info(f"Category {name} seeded successfully with ID {category_id}")
        
        connection.commit()
        logger.info(f"Successfully seeded {len(categories_dict)} categories")
        return categories_dict
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding categories: {e}")
        connection.rollback()
        raise


def seed_sla_policies(connection):
    """ Populate SLA policies for each priority level"""
    cursor = connection.cursor()

    sla_policies_data = [
        ("Standard P1", "P1", 15, 240),
        ("Standard P2", "P2", 60, 480),
        ("Standard P3", "P3", 240, 1440),
        ("Standard P4", "P4", 480, 2880),
    ]

    sla_policies_dict = {}

    try:
        logger.info("Seeding SLA policies...")
        for name, priority, first_response_minutes, resolution_minutes in sla_policies_data:
            cursor.execute("SELECT id FROM sla_policies WHERE name = %s", (name,))
            existing = cursor.fetchone()

            if existing:
                sla_policies_dict[name] = existing[0]
                logger.info(f"SLA policy {name} already exists with ID {existing[0]}")
            else:
                cursor.execute(
                    "INSERT INTO sla_policies (name, priority, first_response_minutes, resolution_minutes) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (name, priority, first_response_minutes, resolution_minutes)
                )
                sla_policy_id = cursor.fetchone()[0]
                sla_policies_dict[name] = sla_policy_id
                logger.info(f"SLA policy {name} seeded successfully with ID {sla_policy_id}")
        
        connection.commit()
        logger.info(f"Successfully seeded {len(sla_policies_dict)} SLA policies")
        return sla_policies_dict
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding SLA policies: {e}")
        connection.rollback()
        raise

def seed_tickets(connection=None, users_dict=None, categories_dict=None, sla_policies_dict=None):
    """ INSERTING 20-30 sample tickets with assorted statuses"""
    cursor = connection.cursor()

    tickets_data = [
        ("VPN connection failing on laptop", "I cannot connect to VPN from my laptop since this morning. Tried restarting but issue persists.", "NEW", "P2", "VPN Issue"),
        ("Email not syncing on mobile", "My work email stopped syncing on my iPhone. Last sync was yesterday evening.", "TRIAGED", "P3", "Email Problem"),
        ("Printer jam in office 3rd floor", "The printer in the 3rd floor break room is jammed. Multiple people affected.", "IN_PROGRESS", "P4", "Printer Issue"),
        ("Cannot access Jira", "Getting 403 error when trying to access Jira. Other team members can access fine.", "WAITING_ON_REQUESTER", "P3", "Application Access"),
        ("Laptop screen flickering", "My laptop screen keeps flickering, making it hard to work. Started 2 days ago.", "RESOLVED", "P2", "Hardware Problem"),
        ("Network outage in building B", "No internet connection in building B. Affecting entire floor.", "NEW", "P1", "Network Issue"),
        ("Suspicious login attempt", "Received email about login from unknown location. Need security team to investigate.", "TRIAGED", "P1", "Security Incident"),
        ("Need access to Salesforce", "New employee needs access to Salesforce CRM. Manager approved.", "NEW", "P3", "Access Request"),
        ("Password expired", "My password expired and I cannot reset it. Getting error message.", "IN_PROGRESS", "P4", "Password Reset"),
        ("Software crash on startup", "Application crashes immediately after opening. Error code: 0x0000005", "WAITING_ON_VENDOR", "P2", "Software Issue"),
        ("WiFi slow in conference room", "WiFi connection is very slow in the main conference room during meetings.", "NEW", "P3", "Network Issue"),
        ("Monitor not displaying", "External monitor connected to laptop but showing no signal. Tried different cables.", "TRIAGED", "P2", "Hardware Problem"),
        ("Cannot send emails", "Can receive emails but cannot send. Getting delivery failure messages.", "IN_PROGRESS", "P2", "Email Problem"),
        ("VPN disconnects frequently", "VPN connection drops every 10-15 minutes. Very disruptive for remote work.", "NEW", "P2", "VPN Issue"),
        ("Printer out of toner", "Printer in marketing department is out of toner. Need replacement.", "RESOLVED", "P4", "Printer Issue"),
        ("Security alert - malware detected", "Antivirus detected potential malware on my system. Quarantined but need review.", "TRIAGED", "P1", "Security Incident"),
        ("Need access to GitHub repository", "New developer needs access to private GitHub repository for project X.", "NEW", "P3", "Access Request"),
        ("Application freezing", "Application freezes when opening large files. System becomes unresponsive.", "IN_PROGRESS", "P2", "Software Issue"),
        ("Network printer offline", "Network printer in accounting department shows as offline. Cannot print invoices.", "WAITING_ON_REQUESTER", "P3", "Printer Issue"),
        ("Email attachment too large", "Cannot send email with large attachment. Getting size limit error.", "NEW", "P4", "Email Problem"),
        ("VPN authentication failed", "VPN authentication keeps failing with 'invalid credentials' error. Credentials are correct.", "TRIAGED", "P2", "VPN Issue"),
        ("Hard drive making noise", "Laptop hard drive making clicking/grinding noise. Concerned about data loss.", "NEW", "P1", "Hardware Problem"),
        ("Cannot access shared drive", "Cannot access the shared network drive. Getting 'access denied' error.", "IN_PROGRESS", "P3", "Network Issue"),
        ("Software license expired", "Application showing license expired message. Need to renew or update license.", "WAITING_ON_VENDOR", "P2", "Software Issue"),
        ("Password reset link not working", "Password reset email link expires immediately or shows error page.", "NEW", "P4", "Password Reset"),
        ("Suspicious email received", "Received phishing email that looks very convincing. Reported but want security review.", "TRIAGED", "P1", "Security Incident"),
        ("Need admin access", "Developer needs admin/root access to server for deployment tasks. Manager approval provided.", "NEW", "P2", "Access Request"),
        ("Application slow performance", "Application running very slowly, taking 30+ seconds to load screens.", "IN_PROGRESS", "P3", "Software Issue"),
        ("Network cable damaged", "Ethernet cable appears damaged. Need replacement cable for workstation.", "RESOLVED", "P4", "Hardware Problem"),
        ("Email rules not working", "Email filtering rules stopped working. Important emails going to spam folder.", "NEW", "P3", "Email Problem"),
    ]

    ticket_statuses = ["NEW", "TRIAGED", "IN_PROGRESS", "WAITING_ON_REQUESTER", "WAITING_ON_VENDOR", "RESOLVED", "CLOSED"]
    ticket_ids = []

    try:
        logger.info("Seeding tickets...")

        # Collect agents to assign
        agents = users_dict.get("AGENT", [])
        requesters = users_dict.get("REQUESTER", [])

        if not requesters:
            raise ValueError("No requesters found")
        
        if not agents:
            raise ValueError("No agents found")
        
        for i, (title, description, status, priority, category_name) in enumerate(tickets_data):
            # Select a random requester
            requester_id = random.choice(requesters)

            # Get the category id
            category_id = categories_dict.get(category_name)
            if not category_id:
                logger.warning(f"Category {category_name} not found, skipping ticket {i+1}")
                continue

            # GET SLA policy id
            sla_policy_id = sla_policies_dict.get(priority)

            #calculate created at some older, some recent
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 24)
            created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

            # Calculate due at based on SLA policy
            due_at = None
            if sla_policy_id:
                cursor.execute(
                    "SELECT resolution_minutes FROM sla_policies WHERE id = %s",
                    (sla_policy_id,)
                )

                result = cursor.fetchone()
                if result:
                    resolution_minutes = result[0]
                    due_at = created_at + timedelta(minutes=resolution_minutes)
            
            #Assign agent for tickets
            assignee_id = None

            if status != "NEW" and agents and random.random() < 0.5:
                assignee_id = random.choice(agents)
            
            #insert ticket
            cursor.execute(
                """INSERT INTO tickets
                (title, description, status, priority, category_id, requester_id, assignee_id, sla_policy_id, created_at, due_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (title, description, status, priority, category_id, requester_id, assignee_id, sla_policy_id, created_at, due_at)
            )
            ticket_id = cursor.fetchone()[0]
            ticket_ids.append(ticket_id)
            logger.info(f"Ticket {title} created successfully with ID {ticket_id}")
        
        connection.commit()
        logger.info(f"Successfully seeded {len(ticket_ids)} tickets")
        return ticket_ids
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding tickets: {e}")
        connection.rollback()
        raise

def seed_comments(connection, ticket_ids, users_dict):
    """ Inserting 15 comments on some tickets"""
    cursor = connection.cursor()

    sample_comments = [
        "Thanks for reporting this. We're looking into it.",
        "Can you provide more details about when this started?",
        "I've escalated this to the network team.",
        "This should be resolved now. Please test and let me know.",
        "Waiting for vendor response. Will update once we hear back.",
        "Internal note: Similar issue reported last week, checking if related.",
        "I'm still experiencing this issue. Any updates?",
        "Issue resolved on my end. You can close this ticket.",
        "I'll be offline this afternoon. Will check back tomorrow.",
        "Can you try restarting your computer and let me know if it helps?",
        "Internal: Need to coordinate with security team before proceeding.",
        "Thanks for the quick response!",
        "I've attached a screenshot showing the error message.",
        "This is affecting multiple users in my department.",
        "Internal: Ticket assigned to network team lead.",
    ]
    
    try:
        logger.info("Seeding comments...")
        comment_count = 0

        # i will add some comments to random tickets
        tickets_with_comments = random.sample(ticket_ids, min(len(ticket_ids), int(len(ticket_ids) * 0.6)))

        all_users = users_dict.get("REQUESTER", []) + users_dict.get("AGENT", []) + users_dict.get("ADMIN", [])

        for ticket_id in tickets_with_comments:
            num_comments = random.randint(1, 3)
            for _ in range(num_comments):
                author_id = random.choice(all_users)
                body = random.choice(sample_comments)
                is_internal = random.random() > 0.7 # 30% chance of internal

                days_ago = random.randint(0, 29)
                hours_ago = random.randint(0, 23)
                created_at = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

                cursor.execute(
                    """INSERT INTO comments (ticket_id, author_id, body, is_internal, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (ticket_id, author_id, body, is_internal, created_at)
                )

                comment_count += 1
        
        connection.commit()
        logger.info(f"Successfully seeded {comment_count} comments")
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding comments: {e}")
        connection.rollback()
        raise

def seed_audit_events(connection, ticket_ids, users_dict):
    """ Inserting some audit events for ticket changes."""
    cursor = connection.cursor()

    try:
        logger.info("Seeding audit events...")
        event_count = 0

        agents = users_dict.get("AGENT", [])
        admins = users_dict.get("ADMIN", [])
        all_actors = agents + admins

        if not all_actors:
            logger.warning("No actors found, skipping audit events")
            return
        
        # Get some tickets to create events for

        tickets_for_events = random.sample(ticket_ids, min(len(ticket_ids), int(len(ticket_ids) * 0.7)))

        for ticket_id in tickets_for_events:
            # Get ticket info

            cursor.execute(
                "SELECT status, assignee_id, priority FROM tickets WHERE id = %s;",
                (ticket_id,)
            )

            ticket_info = cursor.fetchone()
            if not ticket_info:
                continue

            current_status, current_assignee, current_priority = ticket_info

            num_events = random.randint(1, 2)

            for _ in range(num_events):
                actor_id = random.choice(all_actors)
                event_time = datetime.now() - timedelta(days=random.randint(0, 28), hours=random.randint(0, 23))

                # Random event type
                event_type = random.choice(["STATUS_CHANGED", "ASSIGNEE_CHANGED", "PRIORITY_CHANGED"])

                if event_type == "STATUS_CHANGED":
                    old_status = random.choice(["NEW", "TRIAGED", "IN_PROGRESS"])
                    new_status = current_status
                    meta = {"before": old_status, "after": new_status}
                elif event_type == "ASSIGNEE_CHANGED":
                    old_assignee = None if random.random() > 0.5 else random.choice(agents)
                    new_assignee = current_assignee
                    meta = {"before": old_assignee, "after": new_assignee}
                else: # Priority changed
                    old_priority = random.choice(["P1", "P2", "P3", "P4"])
                    new_priority = current_priority
                    meta = {"before": old_priority, "after": new_priority}
                
                cursor.execute(
                    """INSERT INTO audit_events
                    (ticket_id, actor_id, action, meta, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (ticket_id, actor_id, event_type, extras.Json(meta), event_time)
                )

                event_count += 1
        
        connection.commit()
        logger.info(f"Successfully seeded {event_count} audit events")
    
    except psycopg2.Error as e:
        logger.error(f"Error seeding audit events: {e}")
        connection.rollback()
        raise
    except Exception as e:
        logger.error(f"Unexpected error seeding audit events: {e}")
        connection.rollback()
        raise

def main():
    """ Main function to seed the database """
    connection = None
    try:
        logger.info("="*60)
        logger.info("Starting database seeding...")
        logger.info("="*60)

        connection = get_db_connection()

        teams_dict = seed_teams(connection)
        users_dict = seed_users(connection, teams_dict)
        categories_dict = seed_categories(connection)
        sla_policies_dict = seed_sla_policies(connection)
        ticket_ids = seed_tickets(connection, users_dict, categories_dict, sla_policies_dict)
        seed_comments(connection, ticket_ids, users_dict)
        seed_audit_events(connection, ticket_ids, users_dict)

        logger.info("="*60)
        logger.info("Database seeding completed successfully")
        logger.info("="*60)

    except psycopg2.Error as e:
        logger.error(f"Error seeding database: {e}")
        if connection:
            connection.rollback()
        raise
    finally:
        if connection:
            connection.close()
            logger.info("Database connection closed")

if __name__ == "__main__":
    main()



