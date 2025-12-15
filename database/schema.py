def return_create_enums():
    CREATE_ENUMS = """
    -- Creating ENUM types for type saftey
    DO $$ BEGIN
        CREATE TYPE user_role_enum AS ENUM ('REQUESTER', 'AGENT', 'ADMIN');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;

    DO $$ BEGIN
        CREATE TYPE ticket_status_enum AS ENUM (
        'NEW',
        'TRIAGED',
        'IN_PROGRESS',
        'WAITING_ON_REQUESTER',
        'WAITING_ON_VENDOR',
        'RESOLVED',
        'CLOSED',
        'REOPENED'
        );
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;

    DO $$ BEGIN
        CREATE TYPE priority_enum AS ENUM ('P1', 'P2', 'P3', 'P4');
    EXCEPTION
        WHEN duplicate_object THEN NULL;
    END $$;
    """
    return CREATE_ENUMS

def return_create_teams_table():
    CREATE_TEAMS_TABLE = """
    CREATE TABLE IF NOT EXISTS teams (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    return CREATE_TEAMS_TABLE

def return_create_users_table():
    CREATE_USERS_TABLE = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL UNIQUE,
        role user_role_enum NOT NULL,
        team_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE SET NULL
    );
    """
    return CREATE_USERS_TABLE

def return_create_categories_table():
    CREATE_CATEGORIES_TABLE = """
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        default_priority priority_enum NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    return CREATE_CATEGORIES_TABLE

def return_create_sla_policies_table():
    CREATE_SLA_POLICIES_TABLE = """
    CREATE TABLE IF NOT EXISTS sla_policies (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        priority priority_enum NOT NULL,
        first_response_minutes INTEGER NOT NULL,
        resolution_minutes INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    return CREATE_SLA_POLICIES_TABLE

def return_create_tickets_table():
    CREATE_TICKETS_TABLE = """
    CREATE TABLE IF NOT EXISTS tickets (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        status ticket_status_enum NOT NULL DEFAULT 'NEW',
        priority priority_enum NOT NULL,
        category_id INTEGER NOT NULL,
        requester_id INTEGER NOT NULL,
        assignee_id INTEGER,
        sla_policy_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_at TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
        FOREIGN KEY (requester_id) REFERENCES users(id) ON DELETE RESTRICT,
        FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY (sla_policy_id) REFERENCES sla_policies(id) ON DELETE SET NULL
    );
    """
    return CREATE_TICKETS_TABLE

def return_create_comments_table():
    CREATE_COMMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS comments (
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER NOT NULL,
        author_id INTEGER NOT NULL,
        body TEXT NOT NULL,
        is_internal BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
        FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE RESTRICT
    );
    """
    return CREATE_COMMENTS_TABLE

def return_create_attachments_table():
    CREATE_ATTACHMENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS attachments (
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER NOT NULL,
        file_name VARCHAR(255) NOT NULL,
        url TEXT NOT NULL,
        size_bytes BIGINT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
    );
    """
    return CREATE_ATTACHMENTS_TABLE

def return_create_audit_events_table():
    CREATE_AUDIT_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS audit_events (
        id SERIAL PRIMARY KEY,
        ticket_id INTEGER NOT NULL,
        actor_id INTEGER NOT NULL,
        action VARCHAR(255) NOT NULL,
        meta JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
        FOREIGN KEY (actor_id) REFERENCES users(id) ON DELETE RESTRICT
    );
    """
    return CREATE_AUDIT_EVENTS_TABLE

def return_create_indexes():
    CREATE_INDEXES = """
    CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets (status);
    CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets (priority);
    CREATE INDEX IF NOT EXISTS idx_tickets_assignee_id ON tickets (assignee_id);
    CREATE INDEX IF NOT EXISTS idx_tickets_requester_id ON tickets (requester_id);
    CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets (created_at);
    CREATE INDEX IF NOT EXISTS idx_tickets_category_id ON tickets (category_id);
    CREATE INDEX IF NOT EXISTS idx_comments_ticket_id ON comments (ticket_id);
    CREATE INDEX IF NOT EXISTS idx_audit_events_ticket_id ON audit_events (ticket_id);
    CREATE INDEX IF NOT EXISTS idx_audit_events_created_at ON audit_events (created_at);
    """
    return CREATE_INDEXES

def return_create_triggers():
    CREATE_TRIGGERS = """
    -- Function to update the updated_at timestamp
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';

    -- Trigger to auto-update the tickets.updated_at
    DROP TRIGGER IF EXISTS update_tickets_updated_at ON tickets;
    CREATE TRIGGER update_tickets_updated_at
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
    """
    return CREATE_TRIGGERS

def return_drop_schema():
    # This is executes all statements
    DROP_SCHEMA = """
    -- Drop tables in reverse dependency order
    DROP TABLE IF EXISTS audit_events CASCADE;
    DROP TABLE IF EXISTS attachments CASCADE;
    DROP TABLE IF EXISTS comments CASCADE;
    DROP TABLE IF EXISTS tickets CASCADE;
    DROP TABLE IF EXISTS sla_policies CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS teams CASCADE;

    -- Drop ENUM types
    DROP TYPE IF EXISTS ticket_status_enum CASCADE;
    DROP TYPE IF EXISTS priority_enum CASCADE;
    DROP TYPE IF EXISTS user_role_enum CASCADE;
    """
    return DROP_SCHEMA