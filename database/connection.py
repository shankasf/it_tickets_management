import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from .schema import (
    return_create_enums,
    return_create_teams_table,
    return_create_users_table,
    return_create_categories_table,
    return_create_sla_policies_table,
    return_create_tickets_table,
    return_create_comments_table,
    return_create_attachments_table,
    return_create_audit_events_table,
    return_create_indexes,
    return_create_triggers,
    return_drop_schema,
)
import logging

load_dotenv(override=True)
DROP_SCHEMA = return_drop_schema()


# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_user = os.getenv('DB_USER')
        db_name = os.getenv('DB_NAME')
        db_password = os.getenv('DB_PASSWORD')

        if not db_name:
            raise ValueError("DB_NAME is not set in the environment variables")
        if not db_user:
            raise ValueError("DB_USER is not set in the environment variables")
        if not db_password:
            raise ValueError("DB_PASSWORD is not set in the environment variables")
        
        connection = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )

        connection.autocommit = False
        logger.info(f"Connected to database: {db_name}")
        return connection
    
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise
    except ValueError as e:
        logger.error(f"Error: {e}")
        raise

def get_all_schema_statements():
    """ It will return a list of all the schema statements """
    CREATE_ENUMS = return_create_enums()
    CREATE_TEAMS_TABLE = return_create_teams_table()
    CREATE_USERS_TABLE = return_create_users_table()
    CREATE_CATEGORIES_TABLE = return_create_categories_table()
    CREATE_SLA_POLICIES_TABLE = return_create_sla_policies_table()
    CREATE_TICKETS_TABLE = return_create_tickets_table()
    CREATE_COMMENTS_TABLE = return_create_comments_table()
    CREATE_ATTACHMENTS_TABLE = return_create_attachments_table()
    CREATE_AUDIT_EVENTS_TABLE = return_create_audit_events_table()
    CREATE_INDEXES = return_create_indexes()
    CREATE_TRIGGERS = return_create_triggers()
    return [
        CREATE_ENUMS,
        CREATE_TEAMS_TABLE,
        CREATE_USERS_TABLE,
        CREATE_CATEGORIES_TABLE,
        CREATE_SLA_POLICIES_TABLE,
        CREATE_TICKETS_TABLE,
        CREATE_COMMENTS_TABLE,
        CREATE_ATTACHMENTS_TABLE,
        CREATE_AUDIT_EVENTS_TABLE,
        CREATE_INDEXES,
        CREATE_TRIGGERS,
    ]


def init_database(connection=None, drop_existing=False):
    """ Intializes the database by creating all tables, indexes, and triggers.
    """
    conn = connection # get the connection
    should_close = False

    try:
        # Create connection if not provided
        if conn is None:
            conn = get_db_connection()
            should_close = True
        
        cursor = conn.cursor()

        # Drop existing schema if requested
        if drop_existing:
            logger.info("Dropping existing schema...")
            cursor.execute(DROP_SCHEMA)
            conn.commit()
            logger.info("Existing schema dropped successfully")
        
        # Get all schema statements
        schema_statements = get_all_schema_statements()

        # Execute each statements
        logger.info("Creating schema...")
        for i, statement in enumerate(schema_statements, 1):
            try:
                cursor.execute(statement)
                logger.info(f"Executed statement {i}/{len(schema_statements)}: {statement}")
            except psycopg2.Error as e:
                logger.error(f"Error executing statement {i}: {e}")
                logger.error(f"Statement: {statement[:100]}...")
                raise

        conn.commit()
        logger.info("Schema created successfully")

        #verify tables were created
        cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        logger.info(f"Created tables: {[table[0] for table in tables]}")
        
        cursor.close()
        return True
    
    except psycopg2.Error as e:
        logger.error(f"Unexpected error during schema initialization: {e}")
        if conn:
            conn.rollback()
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error during schema initialization: {e}")
        if conn:
            conn.close()
            logger.info("Database connection closed")


def reset_database(connection=None):
    conn = connection
    should_close = False

    try:
        # Create connection if not provided

        if conn is None:
            conn = get_db_connection()
            should_close = True
        
        cursor = conn.cursor()

        logger.info("Resetting database...")
        cursor.execute(DROP_SCHEMA)
        conn.commit()

        logger.info("Database reset successfully")
        cursor.close()
        return True
    
    except psycopg2.Error as e:
        logger.error(f"Unexpected error during database reset: {e}")
        if conn:
            conn.rollback()
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error during database reset: {e}")
        if conn:
            conn.rollback()
        return False
    
    finally:
        if should_close and conn:
            conn.close()

def test_connection():
    """
    Simple function to test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"PostgreSQL version: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

# Main execution block (for testing)
if __name__ == "__main__":
    # Test connection
    print("Testing database connection...")
    if test_connection():
        print("✓ Connection successful!")
        
        # Initialize database
        print("\nInitializing database schema...")
        if init_database(drop_existing=False):
            print("✓ Database schema initialized successfully!")
        else:
            print("✗ Failed to initialize database schema")
    else:
        print("✗ Connection failed. Please check your database configuration.")
