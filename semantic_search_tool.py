#!/usr/bin/env python3
"""
semantic_search_tool.py
Generated: 2025-07-22.0056
Purpose: Add semantic search capability as a new Memory Bank tool

This creates a new tool for semantic-enhanced search that can be integrated
into the existing Memory Bank v04 system.
"""

async def semantic_search_tool(query: str, limit: int = 20, content_types: str = "all", 
                             context_domain: str = None) -> str:
    """
    Semantic-enhanced search across all content types
    
    Expands search queries using semantic equivalents for better discovery.
    Particularly useful for spec workflow terminology.
    """
    global context_manager
    
    if not context_manager or not context_manager.is_initialized():
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    if not query.strip():
        return "❌ Search query cannot be empty."
    
    try:
        # Get semantic expansions for the query
        import json
        
        # Parse query terms
        query_terms = [term.lower().strip() for term in query.split()]
        expanded_terms = []
        expansion_info = []
        
        # Get database connection
        db_path = context_manager.database.db_path
        
        # Check each term for semantic equivalents
        async with context_manager.database._get_connection() as db:
            for term in query_terms:
                # Find semantic matches
                cursor = await db.execute("""
                    SELECT primary_term, equivalent_terms, context_domain, confidence_level 
                    FROM semantic_equivalents 
                    WHERE (primary_term = ? OR equivalent_terms LIKE ?) 
                    AND confidence_level >= 8
                    ORDER BY confidence_level DESC
                    LIMIT 1
                """, (term, f'%"{term}"%'))
                
                row = await cursor.fetchone()
                if row:
                    primary_term, equivalents_json, domain, confidence = row
                    equivalents = json.loads(equivalents_json)
                    
                    # If context domain specified, prefer matches from that domain
                    if context_domain and domain != context_domain:
                        expanded_terms.append(term)
                        continue
                    
                    # Build expanded term with OR clause
                    all_terms = [term, primary_term] + equivalents
                    unique_terms = list(set(all_terms))[:5]  # Limit to 5 terms
                    
                    if len(unique_terms) > 1:
                        expanded_term = f"({' OR '.join(unique_terms)})"
                        expanded_terms.append(expanded_term)
                        expansion_info.append(f"'{term}' → {unique_terms[:3]}")
                    else:
                        expanded_terms.append(term)
                else:
                    expanded_terms.append(term)
        
        # Build enhanced query
        enhanced_query = ' '.join(expanded_terms)
        
        # Perform the search using existing search function
        # Parse content types
        if content_types == "all":
            types_list = None
        else:
            types_list = [t.strip() for t in content_types.split(',')]
        
        # Use the existing full_text_search but with enhanced query
        results = await context_manager.database.full_text_search(
            query=enhanced_query,
            content_types=types_list,
            limit=limit,
            highlight=True
        )
        
        if not results:
            # Try fallback with original query
            results = await context_manager.database.full_text_search(
                query=query,
                content_types=types_list,
                limit=limit,
                highlight=True
            )
            if not results:
                return f"🔍 No results found for: **{query}**\n\n🤖 Semantic expansion attempted but no matches found."
        
        # Format results with semantic enhancement info
        response = f"🔍 **Semantic-Enhanced Search Results for: {query}**\n\n"
        
        if expansion_info:
            response += f"🧠 **Semantic Expansions Applied:**\n"
            for info in expansion_info[:3]:  # Show first 3 expansions
                response += f"   • {info}\n"
            response += "\n"
        
        response += f"📊 Found {len(results)} result(s) • Ranked by relevance\n\n"
        
        # Format results (similar to existing search_all_content)
        current_type = None
        for result in results:
            content_type = result.get('content_type', 'unknown')
            
            # Add content type header
            if content_type != current_type:
                current_type = content_type
                type_icons = {
                    'discussion': '💭',
                    'artifact': '📄',
                    'code_iteration': '⚙️',
                    'plan': '📋',
                    'markdown_file': '📝',
                    'document_v2': '📋'
                }
                icon = type_icons.get(content_type, '📄')
                response += f"## {icon} {content_type.title().replace('_', ' ')}s\n"
            
            # Format individual result
            uuid_short = result.get('uuid', '')[:8]
            title = result.get('title', 'No title')
            created = result.get('created_at', 'Unknown date')
            
            response += f"### **{title}** `[{uuid_short}...]`\n"
            response += f"📅 {created}\n"
            
            # Add highlighted content snippet
            if 'content_highlight' in result and result['content_highlight']:
                snippet = result['content_highlight'][:200] + "..." if len(result['content_highlight']) > 200 else result['content_highlight']
                response += f"💡 {snippet}\n"
            
            # Add spec workflow metadata for documents_v2
            if content_type == 'document_v2':
                document_type = result.get('document_type', 'general')
                importance_score = result.get('importance_score', 5)
                context_domain_result = result.get('context_domain', 'general')
                response += f"🏷️ Type: {document_type}\n"
                if importance_score > 5:
                    response += f"⭐ Importance: {importance_score}/10\n"
                if context_domain_result != 'general':
                    response += f"🔗 Domain: {context_domain_result}\n"
                
                # Add spec workflow metadata if available
                spec_name = result.get('spec_name')
                spec_phase = result.get('spec_phase')
                if spec_name:
                    response += f"📖 Spec: {spec_name}\n"
                if spec_phase:
                    response += f"🔄 Phase: {spec_phase}\n"
            
            response += "\n"
        
        return response
        
    except Exception as e:
        return f"❌ Semantic search failed: {str(e)}"


# Function signature for integration into main.py
SEMANTIC_SEARCH_TOOL_SCHEMA = {
    "name": "semantic_search",
    "description": "Semantic-enhanced search with spec workflow terminology expansion",
    "parameters": {
        "query": {"type": "string", "description": "Search query with semantic expansion"},
        "limit": {"type": "integer", "description": "Maximum results (default: 20)", "default": 20},
        "content_types": {"type": "string", "description": "Content types to search (default: 'all')", "default": "all"},
        "context_domain": {"type": "string", "description": "Preferred semantic domain (spec_workflow, dxt, development)", "required": False}
    }
}

if __name__ == "__main__":
    print("🧠 Semantic Search Tool")
    print("This tool enhances search with spec workflow terminology.")
    print("Integration: Add semantic_search_tool() to main.py tools list")
