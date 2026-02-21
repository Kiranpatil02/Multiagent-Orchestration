

CREATE TABLE IF NOT EXISTS user_requests(
    id  TEXT PRIMARY KEY,
    query TEXT NOT NULL,
    status TEXT NOT NULL,
    -- plan_id TEXT
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
    id    TEXT PRIMARY KEY,
    request_id    TEXT NOT NULL REFERENCES user_requests(id),
    status      TEXT NOT NULL DEFAULT 'ACTIVE',
    -- user_query   TEXT NOT NULL,
    -- max_revisions   INTEGER NOT NULL DEFAULT 3,
    -- revision_count  INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    completed_at  TEXT        
);

CREATE INDEX IF NOT EXISTS idx_plans_request_id ON plans(request_id);
CREATE INDEX IF NOT EXISTS idx_plans_status     ON plans(status);


CREATE TABLE IF NOT EXISTS tasks (
    id      TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES plans(id),
    -- plan_step_id    TEXT NOT NULL REFERENCES plan_steps(id),
    parent_task_id TEXT,
    type         TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'PENDING',
    -- priority      INTEGER NOT NULL DEFAULT 5,
    revision INTEGER DEFAULT 0,
    input_json      TEXT NOT NULL DEFAULT '{}',            
    output_json TEXT,             
    retry_count     INTEGER NOT NULL DEFAULT 0,
    max_retries     INTEGER NOT NULL DEFAULT 3,
    next_run_at  TEXT,
    -- version         INTEGER NOT NULL DEFAULT 1,      
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_status  ON tasks(status);

CREATE TABLE IF NOT EXISTS agent_outputs (
    id       TEXT PRIMARY KEY,
    task_id      TEXT NOT NULL REFERENCES tasks(id),
    -- agent_id   TEXT NOT NULL,
    agent_type    TEXT NOT NULL,
    status        TEXT NOT NULL,
    -- version       INTEGER NOT NULL DEFAULT 1,
    payload_json   TEXT NOT NULL DEFAULT '{}',
    -- confidence_score    INT,                    
    -- error_message TEXT,                    
    -- duration   INTEGER,
    created_at    TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_outputs_task_id    ON agent_outputs(task_id);
CREATE INDEX IF NOT EXISTS idx_outputs_agent_type ON agent_outputs(agent_type);