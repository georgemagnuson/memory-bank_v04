CREATE TABLE unified_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_uuid TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_id INTEGER,
    document_type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active'
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE VIRTUAL TABLE unified_documents_fts USING fts5(
    title, content, summary, tags,
    content='unified_documents',
    content_rowid='id'
)
/* unified_documents_fts(title,content,summary,tags) */;
CREATE TABLE IF NOT EXISTS 'unified_documents_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'unified_documents_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'unified_documents_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'unified_documents_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE TABLE projects (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'  -- JSON metadata
);
CREATE TABLE discussions (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    summary TEXT NOT NULL,
    content TEXT NOT NULL,
    implemented BOOLEAN,  -- True, False, or NULL for unknown
    tags TEXT DEFAULT '[]',  -- JSON array
    chat_session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT,  -- Path to source .md file
    source_file_created TIMESTAMP,  -- File creation time
    source_file_modified TIMESTAMP,  -- File last modified time
    record_status TEXT DEFAULT 'active',  -- 'active', 'superseded', 'obsolete'
    content_signature TEXT,  -- Hash for change detection
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE artifacts (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    artifact_type TEXT DEFAULT 'general',  -- 'code', 'config', 'documentation', etc.
    filename TEXT,
    discussion_uuid TEXT,
    chat_session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT,  -- Path to source .md file
    source_file_created TIMESTAMP,  -- File creation time
    source_file_modified TIMESTAMP,  -- File last modified time
    record_status TEXT DEFAULT 'active',  -- 'active', 'superseded', 'obsolete'
    content_signature TEXT,  -- Hash for change detection
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
    FOREIGN KEY (discussion_uuid) REFERENCES discussions (uuid)
);
CREATE TABLE code_iterations (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    version_number INTEGER DEFAULT 1,
    implemented BOOLEAN DEFAULT FALSE,
    description TEXT DEFAULT '',
    discussion_uuid TEXT,  -- Links to discussions.uuid
    chat_session_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
    FOREIGN KEY (discussion_uuid) REFERENCES discussions (uuid)
);
CREATE TABLE plans (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    phases TEXT DEFAULT '[]',  -- JSON array of phases with tasks and status
    current_phase INTEGER DEFAULT 1,
    overall_status TEXT DEFAULT 'active',  -- 'active', 'completed', 'paused', 'cancelled'
    priority TEXT DEFAULT 'medium',  -- 'high', 'medium', 'low'
    estimated_duration TEXT DEFAULT '',
    actual_progress TEXT DEFAULT '{}',  -- JSON progress tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY,
    session_uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    summary TEXT NOT NULL,
    context_snapshot TEXT DEFAULT '{}',  -- JSON with current state
    next_steps TEXT DEFAULT '',
    status TEXT DEFAULT 'active',  -- 'active', 'completed', 'interrupted'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY,
    source_project_uuid TEXT NOT NULL,
    target_project_uuid TEXT NOT NULL,
    target_item_uuid TEXT NOT NULL,  -- Points to discussions.uuid, artifacts.uuid, etc.
    reference_type TEXT NOT NULL,    -- 'pattern', 'solution', 'approach', 'component'
    context TEXT NOT NULL,          -- Why this reference was made
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE project_context (
    project_uuid TEXT PRIMARY KEY,
    overview TEXT DEFAULT '',         -- Project brief/goals
    current_focus TEXT DEFAULT '',    -- What we're working on now
    recent_progress TEXT DEFAULT '',  -- Last few accomplishments
    active_items TEXT DEFAULT '[]',  -- Current priorities (JSON)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file TEXT,  -- Path to source .md file
    source_file_created TIMESTAMP,  -- File creation time
    source_file_modified TIMESTAMP,  -- File last modified time
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE markdown_files (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    project_uuid TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    content_type TEXT DEFAULT 'markdown',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_created TIMESTAMP,
    file_modified TIMESTAMP,
    content_signature TEXT,
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
CREATE TABLE semantic_equivalents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    primary_term TEXT NOT NULL,
    equivalent_terms TEXT NOT NULL,
    context_domain TEXT NOT NULL DEFAULT 'general',
    confidence_level INTEGER NOT NULL DEFAULT 7,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(primary_term, context_domain)
);
CREATE VIRTUAL TABLE discussions_fts USING fts5(
    uuid,
    summary,
    content,
    tags,
    content='discussions',
    content_rowid='id'
)
/* discussions_fts(uuid,summary,content,tags) */;
CREATE TABLE IF NOT EXISTS 'discussions_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'discussions_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'discussions_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'discussions_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIRTUAL TABLE artifacts_fts USING fts5(
    uuid,
    title,
    content,
    artifact_type,
    filename,
    content='artifacts',
    content_rowid='id'
)
/* artifacts_fts(uuid,title,content,artifact_type,filename) */;
CREATE TABLE IF NOT EXISTS 'artifacts_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'artifacts_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'artifacts_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'artifacts_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIRTUAL TABLE code_iterations_fts USING fts5(
    uuid,
    filename,
    content,
    description,
    content='code_iterations',
    content_rowid='id'
)
/* code_iterations_fts(uuid,filename,content,description) */;
CREATE TABLE IF NOT EXISTS 'code_iterations_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'code_iterations_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'code_iterations_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'code_iterations_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIRTUAL TABLE plans_fts USING fts5(
    uuid,
    title,
    description,
    phases,
    content='plans',
    content_rowid='id'
)
/* plans_fts(uuid,title,description,phases) */;
CREATE TABLE IF NOT EXISTS 'plans_fts_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'plans_fts_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'plans_fts_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'plans_fts_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIRTUAL TABLE markdown_search USING fts5(
    uuid,
    filename,
    file_path,
    content,
    content_type,
    content='markdown_files',
    content_rowid='id'
)
/* markdown_search(uuid,filename,file_path,content,content_type) */;
CREATE TABLE IF NOT EXISTS 'markdown_search_data'(id INTEGER PRIMARY KEY, block BLOB);
CREATE TABLE IF NOT EXISTS 'markdown_search_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS 'markdown_search_docsize'(id INTEGER PRIMARY KEY, sz BLOB);
CREATE TABLE IF NOT EXISTS 'markdown_search_config'(k PRIMARY KEY, v) WITHOUT ROWID;
CREATE VIEW comprehensive_search AS
SELECT 
    'discussion' as content_type,
    uuid,
    summary as title,
    content,
    '' as filename,
    '' as file_path,
    created_at as timestamp
FROM discussions WHERE record_status = 'active'
UNION ALL
SELECT 
    'artifact' as content_type,
    uuid,
    title,
    content,
    filename,
    '' as file_path,
    created_at as timestamp
FROM artifacts WHERE record_status = 'active'
UNION ALL
SELECT 
    'code_iteration' as content_type,
    uuid,
    filename as title,
    content,
    filename,
    '' as file_path,
    created_at as timestamp
FROM code_iterations
UNION ALL
SELECT 
    'plan' as content_type,
    uuid,
    title,
    description as content,
    '' as filename,
    '' as file_path,
    created_at as timestamp
FROM plans WHERE overall_status = 'active'
UNION ALL
SELECT 
    'markdown_file' as content_type,
    uuid,
    filename as title,
    content,
    filename,
    file_path,
    created_at as timestamp
FROM markdown_files
/* comprehensive_search(content_type,uuid,title,content,filename,file_path,timestamp) */;
CREATE INDEX idx_unified_documents_type ON unified_documents(document_type);
CREATE INDEX idx_unified_documents_source ON unified_documents(source_table, source_id);
CREATE INDEX idx_unified_documents_uuid ON unified_documents(original_uuid);
CREATE INDEX idx_unified_documents_status ON unified_documents(status);
CREATE INDEX idx_discussions_project ON discussions(project_uuid);
CREATE INDEX idx_discussions_session ON discussions(chat_session_id);
CREATE INDEX idx_discussions_source_file ON discussions(source_file);
CREATE INDEX idx_discussions_status ON discussions(record_status);
CREATE INDEX idx_artifacts_project ON artifacts(project_uuid);
CREATE INDEX idx_artifacts_source_file ON artifacts(source_file);
CREATE INDEX idx_artifacts_status ON artifacts(record_status);
CREATE INDEX idx_code_iterations_project ON code_iterations(project_uuid);
CREATE INDEX idx_plans_project ON plans(project_uuid);
CREATE INDEX idx_plans_status ON plans(overall_status);
CREATE INDEX idx_sessions_project ON chat_sessions(project_uuid);
CREATE INDEX idx_cross_refs_source ON cross_references(source_project_uuid);
CREATE INDEX idx_markdown_files_project ON markdown_files(project_uuid);
CREATE INDEX idx_markdown_files_path ON markdown_files(file_path);
CREATE INDEX idx_markdown_files_signature ON markdown_files(content_signature);
CREATE INDEX idx_semantic_primary ON semantic_equivalents(primary_term);
CREATE INDEX idx_semantic_domain ON semantic_equivalents(context_domain);
CREATE INDEX idx_semantic_confidence ON semantic_equivalents(confidence_level);
