import os
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse
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
    """
    Get a database connection. Supports both Supabase connection string format
    and traditional PostgreSQL environment variables for backward compatibility.
    
    Priority:
    1. SUPABASE_DB_URL (connection string) - for Supabase
    2. Individual DB_* environment variables - for traditional PostgreSQL
    
    Supabase connection string format:
    postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
    
    Note: If your password contains special characters, make sure they are URL-encoded.
    """
    try:
        # Check for Supabase connection string first (recommended for Supabase)
        supabase_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
        
        if supabase_url:
            logger.info("Connecting to Supabase database using connection string")
            logger.debug(f"Connection string detected (hostname hidden for security)")
            
            # Parse connection string to extract info for logging
            try:
                parsed = urlparse(supabase_url)
                db_host = parsed.hostname
                db_port = parsed.port or 5432
                db_name = parsed.path.lstrip('/') or 'postgres'
                logger.info(f"Connecting to: {db_host}:{db_port}/{db_name}")
            except Exception as parse_err:
                logger.warning(f"Could not parse connection string for logging: {parse_err}")
            
            # Supabase requires SSL - add sslmode=require if not already in the URL
            if 'sslmode=' not in supabase_url:
                # Append sslmode to connection string
                separator = '&' if '?' in supabase_url else '?'
                supabase_url = f"{supabase_url}{separator}sslmode=require"
            
            try:
                connection = psycopg2.connect(
                    supabase_url,
                    connect_timeout=10
                )
            except psycopg2.OperationalError as e:
                # Provide more helpful error messages
                error_msg = str(e).lower()
                if 'ssl' in error_msg or 'certificate' in error_msg:
                    logger.error("SSL connection error. Make sure your connection string includes SSL parameters.")
                    logger.error("Try adding ?sslmode=require to your connection string")
                elif 'password' in error_msg or 'authentication' in error_msg:
                    logger.error("Authentication failed. Please check:")
                    logger.error("1. Your password is correct")
                    logger.error("2. Special characters in password are URL-encoded (e.g., @ becomes %40)")
                    logger.error("3. You're using the correct database user")
                elif 'timeout' in error_msg or 'connection' in error_msg:
                    logger.error("Connection timeout. Please check:")
                    logger.error("1. Your network connection")
                    logger.error("2. The hostname and port are correct")
                    logger.error("3. Your firewall allows connections to Supabase")
                raise
        else:
            # Fallback to traditional PostgreSQL environment variables
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT', '5432')
            db_user = os.getenv('DB_USER')
            db_name = os.getenv('DB_NAME')
            db_password = os.getenv('DB_PASSWORD')

            if not db_name:
                raise ValueError("DB_NAME is not set in the environment variables. For Supabase, use SUPABASE_DB_URL instead.")
            if not db_user:
                raise ValueError("DB_USER is not set in the environment variables. For Supabase, use SUPABASE_DB_URL instead.")
            if not db_password:
                raise ValueError("DB_PASSWORD is not set in the environment variables. For Supabase, use SUPABASE_DB_URL instead.")
            
            logger.info(f"Connecting to PostgreSQL database using individual environment variables")
            logger.info(f"Connecting to: {db_host}:{db_port}/{db_name}")
            connection = psycopg2.connect(
                host=db_host,
                port=db_port,
                database=db_name,
                user=db_user,
                password=db_password
            )

        connection.autocommit = False
        # Get connection info for logging
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT current_database(), inet_server_addr(), inet_server_port();")
            result = cursor.fetchone()
            db_name_actual = result[0] if result else "unknown"
            cursor.close()
            logger.info(f"✓ Successfully connected to database: {db_name_actual}")
        except Exception:
            logger.info("✓ Successfully connected to database")
        
        return connection
    
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error connecting to database: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        raise
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        logger.error(f"Error type: {type(e).__name__}")
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
        # Check environment variables
        supabase_url = os.getenv('SUPABASE_DB_URL') or os.getenv('DATABASE_URL')
        if supabase_url:
            logger.info("✓ Found SUPABASE_DB_URL or DATABASE_URL environment variable")
            # Check if it looks like a valid connection string
            if not supabase_url.startswith(('postgresql://', 'postgres://')):
                logger.warning("⚠ Connection string doesn't start with 'postgresql://' or 'postgres://'")
        else:
            logger.info("✓ Using individual DB_* environment variables")
            required_vars = ['DB_HOST', 'DB_USER', 'DB_NAME', 'DB_PASSWORD']
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                logger.error(f"✗ Missing required environment variables: {', '.join(missing)}")
                return False
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        logger.info(f"✓ PostgreSQL version: {version[0]}")
        
        # Test a simple query
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        logger.info(f"✓ Connected to database: {db_info[0]} as user: {db_info[1]}")
        
        cursor.close()
        conn.close()
        logger.info("✓ Connection test successful!")
        return True
    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        logger.error(f"Error details: {type(e).__name__}")
        import traceback
        logger.debug(traceback.format_exc())
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
