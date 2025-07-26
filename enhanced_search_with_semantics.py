#!/usr/bin/env python3
"""
enhanced_search_with_semantics.py
Generated: 2025-07-22.0055  
Purpose: Enhanced search function that integrates semantic mappings
"""

import json
import aiosqlite
from typing import List, Dict, Any, Set

async def get_semantic_suggestions(db_path: str, term: str, 
                                 context_domain: str = None) -> Dict[str, Any]:
    """
    Get semantic suggestions and related terms for a given term
    """
    suggestions = {
        'original_term': term,
        'related_terms': [],
        'primary_matches': [],
        'equivalent_matches': [],
        'context_domains': [],
        'confidence_levels': []
    }
    
    async with aiosqlite.connect(db_path) as db:
        term_lower = term.lower().strip()
        
        # Find direct primary term matches
        if context_domain:
            cursor = await db.execute("""
                SELECT primary_term, equivalent_terms, context_domain, confidence_level, description
                FROM semantic_equivalents 
                WHERE primary_term = ? AND context_domain = ?
                ORDER BY confidence_level DESC
            """, (term_lower, context_domain))
        else:
            cursor = await db.execute("""
                SELECT primary_term, equivalent_terms, context_domain, confidence_level, description
                FROM semantic_equivalents 
                WHERE primary_term = ?
                ORDER BY confidence_level DESC
            """, (term_lower,))
        
        rows = await cursor.fetchall()
        for row in rows:
            primary_term, equivalents_json, domain, confidence, description = row
            equivalents = json.loads(equivalents_json)
            
            suggestions['primary_matches'].append({
                'term': primary_term,
                'equivalents': equivalents,
                'domain': domain,
                'confidence': confidence,
                'description': description
            })
            suggestions['related_terms'].extend(equivalents)
            suggestions['context_domains'].append(domain)
            suggestions['confidence_levels'].append(confidence)
        
        # Find matches where term appears in equivalents
        cursor = await db.execute("""
            SELECT primary_term, equivalent_terms, context_domain, confidence_level, description
            FROM semantic_equivalents 
            WHERE equivalent_terms LIKE ?
            ORDER BY confidence_level DESC
        """, (f'%"{term_lower}"%',))
        
        rows = await cursor.fetchall()
        for row in rows:
            primary_term, equivalents_json, domain, confidence, description = row
            equivalents = json.loads(equivalents_json)
            
            if term_lower in equivalents:
                suggestions['equivalent_matches'].append({
                    'primary_term': primary_term,
                    'equivalents': equivalents,
                    'domain': domain,
                    'confidence': confidence,
                    'description': description
                })
                suggestions['related_terms'].append(primary_term)
                suggestions['related_terms'].extend([e for e in equivalents if e != term_lower])
                suggestions['context_domains'].append(domain)
                suggestions['confidence_levels'].append(confidence)
    
    # Remove duplicates and sort
    suggestions['related_terms'] = sorted(list(set(suggestions['related_terms'])))
    suggestions['context_domains'] = sorted(list(set(suggestions['context_domains'])))
    suggestions['confidence_levels'] = sorted(list(set(suggestions['confidence_levels'])), reverse=True)
    
    return suggestions

# Test the semantic suggestions
async def test_semantic_suggestions():
    db_path = '/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db'
    
    test_terms = ['requirements', 'design', 'dxt', 'dependencies', 'workflow']
    
    print("🧪 Testing Semantic Suggestions:")
    print("=" * 50)
    
    for term in test_terms:
        suggestions = await get_semantic_suggestions(db_path, term)
        print(f"\n🔍 Term: '{term}'")
        print(f"📋 Related terms: {suggestions['related_terms'][:7]}")
        print(f"🏷️  Domains: {suggestions['context_domains']}")
        print(f"⭐ Confidence levels: {suggestions['confidence_levels']}")
        
        if suggestions['primary_matches']:
            print(f"🎯 Primary match: {suggestions['primary_matches'][0]['description']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_semantic_suggestions())
