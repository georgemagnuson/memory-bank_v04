#!/usr/bin/env python3
"""
semantic_mappings_implementation.py
Generated: 2025-07-22.0054
Purpose: Implement spec workflow semantic mappings for Memory Bank v04

This file contains the implementation for adding semantic search capabilities
to enhance spec workflow terminology discovery and cross-reference.
"""

import sqlite3
import json
import logging
from typing import List, Dict, Set

logger = logging.getLogger("memory_bank_mcp.semantic_mappings")

# Spec workflow semantic mappings
SPEC_WORKFLOW_SEMANTICS = {
    "requirements": {
        "equivalents": [
            "user_stories", "acceptance_criteria", "EARS", "functional_requirements", 
            "specifications", "needs", "business_requirements", "use_cases",
            "feature_requirements", "system_requirements", "constraints"
        ],
        "context_domain": "spec_workflow",
        "confidence": 9,
        "description": "Requirements gathering and specification phase"
    },
    "design": {
        "equivalents": [
            "architecture", "mermaid", "components", "interfaces", "data_models",
            "technical_design", "system_design", "ui_design", "database_design",
            "api_design", "wireframes", "mockups", "prototypes", "blueprints"
        ],
        "context_domain": "spec_workflow", 
        "confidence": 9,
        "description": "Design and architecture phase"
    },
    "tasks": {
        "equivalents": [
            "implementation", "subtasks", "atomic_tasks", "test_driven", 
            "task_breakdown", "work_items", "todos", "action_items",
            "development_tasks", "coding_tasks", "tickets", "issues"
        ],
        "context_domain": "spec_workflow",
        "confidence": 9,
        "description": "Task breakdown and planning phase"
    },
    "implementation": {
        "equivalents": [
            "execute", "develop", "code", "build", "create", "construct",
            "coding", "programming", "development", "construction", 
            "deployment", "delivery", "realization"
        ],
        "context_domain": "spec_workflow",
        "confidence": 9,
        "description": "Implementation and execution phase"
    },
    "workflow": {
        "equivalents": [
            "spec", "specification", "feature", "development", "methodology",
            "process", "pipeline", "sequence", "procedure", "framework",
            "approach", "strategy", "plan"
        ],
        "context_domain": "spec_workflow",
        "confidence": 8,
        "description": "General workflow and process terms"
    },
    "template": {
        "equivalents": [
            "pattern", "blueprint", "boilerplate", "scaffold", "skeleton",
            "framework", "structure", "format", "model", "example",
            "starter", "baseline", "foundation"
        ],
        "context_domain": "spec_workflow",
        "confidence": 8,
        "description": "Templates and reusable patterns"
    },
    "documentation": {
        "equivalents": [
            "docs", "guide", "manual", "reference", "handbook", "readme",
            "specification", "description", "explanation", "notes",
            "instructions", "guidelines", "standards"
        ],
        "context_domain": "spec_workflow",
        "confidence": 7,
        "description": "Documentation and reference materials"
    }
}

# Additional semantic mappings for development context
DEVELOPMENT_SEMANTICS = {
    "django": {
        "equivalents": [
            "python_web", "web_framework", "mvc", "models", "views", "templates",
            "orm", "django_rest", "drf", "admin", "migrations", "settings"
        ],
        "context_domain": "development",
        "confidence": 9,
        "description": "Django web framework terminology"
    },
    "database": {
        "equivalents": [
            "db", "sql", "sqlite", "postgresql", "mysql", "schema", "tables",
            "queries", "orm", "models", "migrations", "indexes", "relations"
        ],
        "context_domain": "development", 
        "confidence": 8,
        "description": "Database and data storage terms"
    },
    "frontend": {
        "equivalents": [
            "ui", "ux", "javascript", "react", "vue", "angular", "css", "html",
            "bootstrap", "tailwind", "responsive", "mobile", "client_side"
        ],
        "context_domain": "development",
        "confidence": 8,
        "description": "Frontend and user interface terms"
    }
}

# DXT and installation related semantics
DXT_SEMANTICS = {
    "dxt": {
        "equivalents": [
            "desktop_extension", "claude_extension", "mcp_server", "installation",
            "package", "bundled_dependencies", "manifest", "distribution"
        ],
        "context_domain": "dxt",
        "confidence": 9,
        "description": "DXT (Desktop Extensions) terminology"
    },
    "dependencies": {
        "equivalents": [
            "packages", "libraries", "modules", "requirements", "installations",
            "pip_install", "bundled", "vendor", "lib", "node_modules"
        ],
        "context_domain": "dxt",
        "confidence": 8,
        "description": "Dependencies and package management"
    }
}

def create_semantic_equivalents_table_sql() -> str:
    """Generate SQL to create semantic equivalents table"""
    return """
    CREATE TABLE IF NOT EXISTS semantic_equivalents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        primary_term TEXT NOT NULL,
        equivalent_terms TEXT NOT NULL,  -- JSON array of equivalent terms
        context_domain TEXT NOT NULL DEFAULT 'general',
        confidence_level INTEGER NOT NULL DEFAULT 7,  -- 1-10 scale
        description TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(primary_term, context_domain)
    );
    
    CREATE INDEX IF NOT EXISTS idx_semantic_primary ON semantic_equivalents(primary_term);
    CREATE INDEX IF NOT EXISTS idx_semantic_domain ON semantic_equivalents(context_domain);
    CREATE INDEX IF NOT EXISTS idx_semantic_confidence ON semantic_equivalents(confidence_level);
    """

def get_semantic_mappings_insert_sql() -> List[str]:
    """Generate SQL INSERT statements for all semantic mappings"""
    inserts = []
    
    # Add spec workflow semantics
    for term, data in SPEC_WORKFLOW_SEMANTICS.items():
        inserts.append(f"""
        INSERT OR REPLACE INTO semantic_equivalents 
        (primary_term, equivalent_terms, context_domain, confidence_level, description)
        VALUES (
            '{term}',
            '{json.dumps(data["equivalents"])}',
            '{data["context_domain"]}',
            {data["confidence"]},
            '{data["description"]}'
        );
        """)
    
    # Add development semantics  
    for term, data in DEVELOPMENT_SEMANTICS.items():
        inserts.append(f"""
        INSERT OR REPLACE INTO semantic_equivalents 
        (primary_term, equivalent_terms, context_domain, confidence_level, description)
        VALUES (
            '{term}',
            '{json.dumps(data["equivalents"])}',
            '{data["context_domain"]}',
            {data["confidence"]},
            '{data["description"]}'
        );
        """)
    
    # Add DXT semantics
    for term, data in DXT_SEMANTICS.items():
        inserts.append(f"""
        INSERT OR REPLACE INTO semantic_equivalents 
        (primary_term, equivalent_terms, context_domain, confidence_level, description)
        VALUES (
            '{term}',
            '{json.dumps(data["equivalents"])}',
            '{data["context_domain"]}',
            {data["confidence"]},
            '{data["description"]}'
        );
        """)
    
    return inserts

class SemanticSearchExpander:
    """Expands search queries using semantic equivalents"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._cache = {}
        
    async def load_semantic_mappings(self) -> Dict[str, List[str]]:
        """Load all semantic mappings from database"""
        if self._cache:
            return self._cache
            
        import aiosqlite
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT primary_term, equivalent_terms, context_domain, confidence_level
                FROM semantic_equivalents
                ORDER BY confidence_level DESC
            """)
            
            rows = await cursor.fetchall()
            
            # Build cache
            for row in rows:
                term = row[0]
                equivalents = json.loads(row[1])
                domain = row[2]
                confidence = row[3]
                
                key = f"{term}:{domain}"
                self._cache[key] = {
                    'equivalents': equivalents,
                    'confidence': confidence
                }
                
                # Also add reverse mappings for high confidence terms
                if confidence >= 8:
                    for equiv in equivalents:
                        reverse_key = f"{equiv}:{domain}"
                        if reverse_key not in self._cache:
                            self._cache[reverse_key] = {
                                'equivalents': [term] + [e for e in equivalents if e != equiv],
                                'confidence': confidence - 1  # Slightly lower confidence for reverse
                            }
        
        return self._cache
    
    async def expand_query(self, query: str, context_domain: str = None) -> str:
        """
        Expand search query with semantic equivalents
        
        Args:
            query: Original search query
            context_domain: Preferred context domain for expansion
            
        Returns:
            Expanded query with OR clauses for semantic equivalents
        """
        await self.load_semantic_mappings()
        
        # Split query into individual terms
        terms = query.lower().split()
        expanded_terms = []
        
        for term in terms:
            expanded_term_set = {term}  # Start with original term
            
            # Check for direct matches
            for key, data in self._cache.items():
                cached_term, cached_domain = key.split(':', 1)
                
                # Skip if context domain specified and doesn't match
                if context_domain and cached_domain != context_domain:
                    continue
                    
                # Check if term matches primary term or equivalent
                if (term == cached_term or 
                    term in data['equivalents'] or 
                    any(term in equiv for equiv in data['equivalents'])):
                    
                    # Add equivalents based on confidence
                    if data['confidence'] >= 8:
                        expanded_term_set.update(data['equivalents'])
                        expanded_term_set.add(cached_term)
            
            # Build OR clause for this term
            if len(expanded_term_set) > 1:
                # Create OR clause with original term having highest priority
                expanded_terms.append(f"({' OR '.join(sorted(expanded_term_set))})")
            else:
                expanded_terms.append(term)
        
        return ' '.join(expanded_terms)
    
    async def suggest_related_terms(self, term: str, context_domain: str = None) -> List[str]:
        """Get related terms for a given term"""
        await self.load_semantic_mappings()
        
        related = set()
        term_lower = term.lower()
        
        for key, data in self._cache.items():
            cached_term, cached_domain = key.split(':', 1)
            
            if context_domain and cached_domain != context_domain:
                continue
                
            if (term_lower == cached_term or 
                term_lower in data['equivalents']):
                related.update(data['equivalents'])
                related.add(cached_term)
        
        # Remove the original term and return sorted list
        related.discard(term_lower)
        return sorted(list(related))


# Test function to verify semantic mappings
async def test_semantic_mappings(db_path: str):
    """Test the semantic mappings implementation"""
    expander = SemanticSearchExpander(db_path)
    
    test_queries = [
        "requirements",
        "design architecture", 
        "task breakdown",
        "implementation code",
        "dxt installation",
        "django models"
    ]
    
    print("🧪 Testing Semantic Query Expansion:\n")
    
    for query in test_queries:
        expanded = await expander.expand_query(query)
        related = await expander.suggest_related_terms(query.split()[0])
        
        print(f"Query: '{query}'")
        print(f"Expanded: '{expanded}'")
        print(f"Related terms: {related[:5]}")  # Show first 5
        print()

if __name__ == "__main__":
    import asyncio
    
    # Example usage
    db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
    asyncio.run(test_semantic_mappings(db_path))
