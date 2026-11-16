"""Database schema statements and default records for AUTONOM."""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'idle',
        current_task TEXT,
        model TEXT NOT NULL,
        tasks_completed INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        agent_id TEXT,
        task_type TEXT NOT NULL,
        priority TEXT NOT NULL DEFAULT 'normal',
        status TEXT NOT NULL DEFAULT 'queued',
        parameters_json TEXT,
        result_json TEXT,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (agent_id) REFERENCES agents (id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        external_id TEXT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        location TEXT NOT NULL,
        remote_type TEXT NOT NULL DEFAULT 'hybrid',
        salary_min INTEGER,
        salary_max INTEGER,
        currency TEXT NOT NULL DEFAULT 'USD',
        url TEXT NOT NULL,
        platform TEXT NOT NULL,
        description TEXT,
        match_score REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'discovered',
        posted_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS applications (
        id TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        tailored_resume_path TEXT,
        cover_letter TEXT,
        submission_receipt_path TEXT,
        submitted_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY,
        task_id TEXT,
        agent_id TEXT,
        tier INTEGER NOT NULL DEFAULT 3,
        action_type TEXT NOT NULL,
        target_resource TEXT NOT NULL,
        summary TEXT NOT NULL,
        details_json TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        resolved_by TEXT,
        FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        agent_id TEXT,
        task_id TEXT,
        action TEXT NOT NULL,
        pre_state_hash TEXT,
        post_state_hash TEXT,
        metadata_json TEXT
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS credentials (
        id TEXT PRIMARY KEY,
        service_name TEXT NOT NULL UNIQUE,
        account_identifier TEXT,
        value_encrypted BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_jobs_platform ON jobs(platform);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
    """
]

DEFAULT_AGENTS = [
    {
        "id": "coordinator-01",
        "name": "Lead Coordinator",
        "role": "Orchestrator",
        "status": "idle",
        "model": "gpt-4o",
    },
    {
        "id": "scout-01",
        "name": "Job Scout",
        "role": "Discovery & Scraping",
        "status": "idle",
        "model": "gpt-4o-mini",
    },
    {
        "id": "tailor-01",
        "name": "Resume Tailor",
        "role": "Document Generator",
        "status": "idle",
        "model": "claude-3-5-sonnet",
    },
    {
        "id": "submitter-01",
        "name": "Application Submitter",
        "role": "Computer Interaction",
        "status": "idle",
        "model": "claude-3-5-sonnet",
    },
]
