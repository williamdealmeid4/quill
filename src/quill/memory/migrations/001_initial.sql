-- Quill schema v1. Applied as one explicit transaction by the storage worker.
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    role TEXT NOT NULL CHECK(role IN ('user','assistant','tool','system')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    task_id TEXT REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id),
    submission_id TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL CHECK(state IN ('queued','preparing','running','awaiting_approval','verifying','awaiting_review','applying','succeeded','failed','cancelled','interrupted','blocked')),
    mode TEXT NOT NULL CHECK(mode IN ('read','assisted','restricted_auto')),
    project_path TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    error_json TEXT
);

CREATE TABLE IF NOT EXISTS task_events (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    sequence INTEGER NOT NULL CHECK(sequence>=0),
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    UNIQUE(task_id,sequence)
);

CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    backend TEXT NOT NULL,
    thread_id TEXT,
    turn_id TEXT,
    model TEXT NOT NULL,
    effort TEXT NOT NULL,
    cli_version TEXT NOT NULL,
    schema_digest TEXT NOT NULL,
    state TEXT NOT NULL,
    started_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS workspaces (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    source_path TEXT NOT NULL,
    root_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workspace_files (
    workspace_id TEXT NOT NULL REFERENCES workspaces(id),
    relative_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size INTEGER NOT NULL CHECK(size>=0),
    executable INTEGER NOT NULL CHECK(executable IN (0,1)),
    PRIMARY KEY(workspace_id,relative_path)
);

CREATE TABLE IF NOT EXISTS changesets (
    id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL REFERENCES workspaces(id),
    digest TEXT NOT NULL,
    manifest_json TEXT NOT NULL,
    diff_path TEXT NOT NULL,
    verification_json TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS permission_grants (
    id TEXT PRIMARY KEY,
    mode TEXT NOT NULL,
    scope_json TEXT NOT NULL,
    arguments_digest TEXT,
    expires_at TEXT NOT NULL,
    revoked_at TEXT,
    quota_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS approval_requests (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    action_json TEXT NOT NULL,
    action_digest TEXT NOT NULL,
    state TEXT NOT NULL,
    requested_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    resolved_at TEXT
);

CREATE TABLE IF NOT EXISTS tool_runs (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL REFERENCES tasks(id),
    tool_name TEXT NOT NULL,
    action_digest TEXT NOT NULL,
    state TEXT NOT NULL,
    result_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    schema_version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    checksum TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_state_created ON tasks(state,created_at,id);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id,created_at,id);
CREATE INDEX IF NOT EXISTS idx_executions_task ON executions(task_id);
CREATE INDEX IF NOT EXISTS idx_approvals_state_expires ON approval_requests(state,expires_at);
