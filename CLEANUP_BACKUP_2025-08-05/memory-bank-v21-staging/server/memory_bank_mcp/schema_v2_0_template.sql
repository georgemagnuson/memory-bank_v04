-- Memory Bank v2.0 Enhanced Schema Template
-- Generated: 2025-08-03.0023
-- Purpose: Complete v2.0 schema for new project initialization
-- Features: Composite primary keys, document versioning, cross-project support

-- Core Projects Table
CREATE TABLE projects (
    uuid TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    description TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT DEFAULT '{}'  -- JSON metadata
);

-- v2.0 Documents Table with Composite Primary Key and Versioning
CREATE TABLE documents (
    project_uuid TEXT NOT NULL,          -- Links to projects.uuid
    uuid TEXT NOT NULL,                  -- Document UUID within project
    version INTEGER NOT NULL DEFAULT 1,  -- Document versioning system
    document_type TEXT NOT NULL,         -- 'discussion', 'artifact', 'plan', etc.
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',          -- Legacy source_table/source_id here
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by TEXT,
    status TEXT DEFAULT 'active',
    
    PRIMARY KEY (project_uuid, uuid, version),
    FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
);

-- Performance Indexes for v2.0 Documents
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_project ON documents(project_uuid);
CREATE INDEX idx_documents_uuid_latest ON documents(uuid, version);
CREATE INDEX idx_documents_created ON documents(created_at);
CREATE INDEX idx_documents_status ON documents(status);

-- Chat Sessions for Session Management
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

CREATE INDEX idx_sessions_project ON chat_sessions(project_uuid);

-- Cross-Project References
CREATE TABLE cross_references (
    id INTEGER PRIMARY KEY,
    source_project_uuid TEXT NOT NULL,
    target_project_uuid TEXT NOT NULL,
    target_item_uuid TEXT NOT NULL,  -- Points to documents.uuid
    reference_type TEXT NOT NULL,    -- 'pattern', 'solution', 'approach', 'component'
    context TEXT NOT NULL,          -- Why this reference was made
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_project_uuid) REFERENCES projects (uuid)
);

CREATE INDEX idx_cross_refs_source ON cross_references(source_project_uuid);

-- Project Context Management
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

-- Markdown Files Support
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

CREATE INDEX idx_markdown_files_project ON markdown_files(project_uuid);
CREATE INDEX idx_markdown_files_path ON markdown_files(file_path);
CREATE INDEX idx_markdown_files_signature ON markdown_files(content_signature);

-- Full-Text Search for Markdown
CREATE VIRTUAL TABLE markdown_search USING fts5(
    uuid,
    filename,
    file_path,
    content,
    content_type,
    content='markdown_files',
    content_rowid='id'
);

-- Semantic Equivalents for Enhanced Search
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

CREATE INDEX idx_semantic_primary ON semantic_equivalents(primary_term);
CREATE INDEX idx_semantic_domain ON semantic_equivalents(context_domain);
CREATE INDEX idx_semantic_confidence ON semantic_equivalents(confidence_level);

-- Comprehensive Search (Future Enhancement)
CREATE TABLE comprehensive_search (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query TEXT NOT NULL,
    results TEXT NOT NULL, -- JSON array of search results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Memory Bank v2.0 Schema Complete
-- Total Tables: 10 core tables + 5 FTS/index tables = 15 total
-- Key Features: Composite primary keys, document versioning, cross-project support, performance optimized
