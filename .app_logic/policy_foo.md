# PolicyFoo App Specification

## Purpose
LLM workflow for answering policy/regulation questions with citations.

## Current Status
- Initial app structure created
- URL routing configured
- Models defined (PolicyDocument, PolicyQuery, PolicyResponse)
- Placeholder views created

## Planned Features
- Bootstrap-styled chat interface with citations
- RAG over policy documents
- Response validation against sources
- Export capability for answers
- Rate limiting

## Components
1. **Models** (Defined)
   - PolicyDocument - Stores policy documents with title, content, and document_id
   - PolicyQuery - Stores user queries with query_text and user_identifier
   - PolicyResponse - Stores responses with reference to query and documents

2. **Views** (Placeholder)
   - ChatInterfaceView - Will provide the policy chat interface
   - DocumentSearchView - Will allow searching policy documents
   - PolicyRetrieverView - API endpoint for policy retrieval

3. **Future Components**
   - PolicyRetriever service
   - CitationGenerator service
   - Templates for chat interface and document search

## Integration Points
- Will use the same base template as other apps
- Will share rate limiting approach with PaceNoteFoo
- Will use Bootstrap for consistent styling

## Questions
1. What specific policy documents need to be included?
2. Required response format (Markdown/plain text)?
3. Any audit requirements for queries/responses?