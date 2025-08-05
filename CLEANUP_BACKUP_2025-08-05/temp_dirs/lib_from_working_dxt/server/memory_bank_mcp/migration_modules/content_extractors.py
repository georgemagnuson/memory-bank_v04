"""
migration_modules/content_extractors.py
Generated: 2025-07-29.2316
Purpose: Content extraction utilities for Memory Bank v2.0 migration
Handles pattern extraction, decision parsing, and content classification
"""

import re
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.migration.extractors")


class ContentExtractors:
    """Content extraction utilities for unified document migration"""
    
    @staticmethod
    def extract_artifact_patterns(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract patterns from systemPatterns.md or similar files
        Converts to artifact-type documents in unified architecture
        """
        patterns = []
        
        # Pattern 1: ## Pattern Name followed by content
        pattern_sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        if len(pattern_sections) > 1:
            for i in range(1, len(pattern_sections), 2):
                if i + 1 < len(pattern_sections):
                    pattern_name = pattern_sections[i].strip()
                    pattern_content = pattern_sections[i + 1].strip()
                    
                    if pattern_content:
                        patterns.append({
                            'title': f"Pattern: {pattern_name}",
                            'content': pattern_content,
                            'document_type': 'artifact',
                            'source_file': str(file_path),
                            'pattern_type': 'system_pattern',
                            'extracted_from': 'systemPatterns.md'
                        })
        
        # Pattern 2: Code blocks with preceding context
        code_pattern = r'(?:^|\n)([^\n]*?)\n```(?:(\w+))?\n(.*?)```'
        for match in re.finditer(code_pattern, content, re.DOTALL):
            context, language, code = match.groups()
            
            if code.strip():
                title = f"Code Pattern: {context.strip()[:50]}" if context.strip() else f"Code Pattern from {file_path.name}"
                
                patterns.append({
                    'title': title,
                    'content': f"**Context:** {context.strip()}\n\n**Language:** {language or 'text'}\n\n```{language or ''}\n{code.strip()}\n```",
                    'document_type': 'artifact',
                    'source_file': str(file_path),
                    'pattern_type': 'code_pattern',
                    'language': language or 'text'
                })
        
        logger.info(f"Extracted {len(patterns)} patterns from {file_path.name}")
        return patterns
    
    @staticmethod
    def extract_discussion_items(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract discussion items from progress.md or journal files
        Converts to discussion-type documents in unified architecture
        """
        discussions = []
        
        # Pattern 1: ## Date or ## Topic sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        if len(sections) > 1:
            for i in range(1, len(sections), 2):
                if i + 1 < len(sections):
                    section_title = sections[i].strip()
                    section_content = sections[i + 1].strip()
                    
                    if section_content:
                        discussions.append({
                            'title': f"Discussion: {section_title}",
                            'content': section_content,
                            'document_type': 'discussion',
                            'source_file': str(file_path),
                            'discussion_type': 'progress_update',
                            'date_extracted': datetime.now(timezone.utc).isoformat()
                        })
        
        # Pattern 2: Bullet points with decisions
        decision_pattern = r'(?:^|\n)[-*] (.+?)(?=\n[-*]|\n\n|\Z)'
        for match in re.finditer(decision_pattern, content, re.DOTALL):
            item_content = match.group(1).strip()
            
            # Look for decision indicators
            if any(indicator in item_content.lower() for indicator in ['decided', 'agreed', 'resolved', 'concluded']):
                discussions.append({
                    'title': f"Decision: {item_content[:50]}...",
                    'content': item_content,
                    'document_type': 'discussion',
                    'source_file': str(file_path),
                    'discussion_type': 'decision',
                    'decision_made': True
                })
        
        logger.info(f"Extracted {len(discussions)} discussion items from {file_path.name}")
        return discussions
    
    @staticmethod
    def extract_journal_decisions(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract decisions from journal entries
        These become separate decision records (not unified documents)
        """
        decisions = []
        
        # Look for decision patterns
        decision_patterns = [
            r'(?:^|\n)(?:DECISION|Decision):\s*(.+?)(?=\n(?:[A-Z]+:|$)|\n\n|\Z)',
            r'(?:^|\n)(?:DECIDED|Decided):\s*(.+?)(?=\n(?:[A-Z]+:|$)|\n\n|\Z)',
            r'(?:^|\n)(?:RESOLVED|Resolved):\s*(.+?)(?=\n(?:[A-Z]+:|$)|\n\n|\Z)'
        ]
        
        for pattern in decision_patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                decision_content = match.group(1).strip()
                
                if decision_content:
                    decisions.append({
                        'summary': decision_content[:200],  # First 200 chars as summary
                        'full_content': decision_content,
                        'source_file': str(file_path),
                        'decision_type': 'journal_entry',
                        'extracted_at': datetime.now(timezone.utc).isoformat()
                    })
        
        logger.info(f"Extracted {len(decisions)} decisions from {file_path.name}")
        return decisions
    
    @staticmethod
    def extract_rules(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extract rules from global_rules.md or .membankrules
        Converts to artifact-type documents in unified architecture
        """
        rules = []
        
        if file_path.name == '.membankrules':
            # Handle config-style rules
            rules.extend(ContentExtractors._extract_config_rules(content, file_path))
        else:
            # Handle markdown-style rules
            rules.extend(ContentExtractors._extract_markdown_rules(content, file_path))
        
        logger.info(f"Extracted {len(rules)} rules from {file_path.name}")
        return rules
    
    @staticmethod
    def _extract_markdown_rules(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from markdown format"""
        rules = []
        
        # Pattern 1: ## Rule Name sections
        rule_sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)
        
        if len(rule_sections) > 1:
            for i in range(1, len(rule_sections), 2):
                if i + 1 < len(rule_sections):
                    rule_name = rule_sections[i].strip()
                    rule_content = rule_sections[i + 1].strip()
                    
                    if rule_content:
                        rules.append({
                            'title': f"Rule: {rule_name}",
                            'content': rule_content,
                            'document_type': 'artifact',
                            'source_file': str(file_path),
                            'artifact_type': 'rule',
                            'rule_category': 'project_rule'
                        })
        
        # Pattern 2: Numbered or bulleted rules
        rule_pattern = r'(?:^|\n)(?:\d+\.|[-*]) (.+?)(?=\n(?:\d+\.|\n|[-*])|\Z)'
        for match in re.finditer(rule_pattern, content, re.DOTALL):
            rule_content = match.group(1).strip()
            
            if len(rule_content) > 10:  # Only substantial rules
                rules.append({
                    'title': f"Rule: {rule_content[:50]}...",
                    'content': rule_content,
                    'document_type': 'artifact',
                    'source_file': str(file_path),
                    'artifact_type': 'rule',
                    'rule_category': 'project_rule'
                })
        
        return rules
    
    @staticmethod
    def _extract_config_rules(content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from config-style format (.membankrules)"""
        rules = []
        
        # Simple line-based rules
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Handle key=value format
            if '=' in line:
                key, value = line.split('=', 1)
                rules.append({
                    'title': f"Config Rule: {key.strip()}",
                    'content': f"**Setting:** {key.strip()}\n**Value:** {value.strip()}",
                    'document_type': 'artifact',
                    'source_file': str(file_path),
                    'artifact_type': 'config_rule',
                    'rule_category': 'configuration'
                })
            else:
                # Handle simple statements
                rules.append({
                    'title': f"Rule: {line[:50]}...",
                    'content': line,
                    'document_type': 'artifact',
                    'source_file': str(file_path),
                    'artifact_type': 'rule',
                    'rule_category': 'configuration'
                })
        
        return rules
    
    @staticmethod
    def classify_markdown_content(content: str, file_path: Path) -> Dict[str, Any]:
        """
        Classify markdown content for document type assignment
        Returns classification with confidence scores
        """
        filename_lower = file_path.name.lower()
        
        # Initialize scores
        artifact_score = 0
        discussion_score = 0
        plan_score = 0
        code_score = 0
        note_score = 0
        
        # Content analysis
        code_blocks = len(re.findall(r'```', content))
        task_items = len(re.findall(r'(?:^|\n)[-*] \[ \]', content))
        decision_markers = len(re.findall(r'(?:decided|decision|resolved|agreed)', content, re.IGNORECASE))
        sections = len(re.findall(r'^## ', content, re.MULTILINE))
        
        # Filename-based scoring
        if any(keyword in filename_lower for keyword in ['pattern', 'template', 'rule', 'config']):
            artifact_score += 3
        if any(keyword in filename_lower for keyword in ['progress', 'journal', 'meeting', 'discussion']):
            discussion_score += 3
        if any(keyword in filename_lower for keyword in ['plan', 'roadmap', 'strategy', 'brief']):
            plan_score += 3
        if any(keyword in filename_lower for keyword in ['note', 'scratch', 'idea']):
            note_score += 2
        
        # Content-based scoring
        if code_blocks > 2:
            code_score += 3
            artifact_score += 1
        if task_items > 0:
            discussion_score += 2
            plan_score += 1
        if decision_markers > 2:
            discussion_score += 3
        if sections > 3:
            artifact_score += 1
            plan_score += 1
        
        # Determine classification
        scores = {
            'artifact': artifact_score,
            'discussion': discussion_score,
            'plan': plan_score,
            'code': code_score,
            'note': note_score
        }
        
        # Find highest score
        max_score = max(scores.values())
        if max_score == 0:
            document_type = 'note'  # Default fallback
        else:
            document_type = max(scores, key=scores.get)
        
        return {
            'document_type': document_type,
            'confidence': max_score,
            'scores': scores,
            'content_indicators': {
                'code_blocks': code_blocks,
                'task_items': task_items,
                'decision_markers': decision_markers,
                'sections': sections
            }
        }
    
    @staticmethod
    def generate_content_signature(content: str) -> str:
        """Generate content signature for duplicate detection"""
        # Normalize content for signature generation
        normalized = re.sub(r'\s+', ' ', content.strip().lower())
        return hashlib.md5(normalized.encode()).hexdigest()
