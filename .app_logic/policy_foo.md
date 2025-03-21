# PolicyFoo App Specification

## Purpose
LLM workflow for answering policy/regulation questions with citations.

## Current Status
- Initial app structure created
- URL routing configured
- Models defined (PolicyDocument, PolicyQuery, PolicyResponse)
- Placeholder views created
- Document search template implemented

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

2. **Views** (Implementation In Progress)
   - ChatInterfaceView - Will provide the policy chat interface (Placeholder)
   - DocumentSearchView - Search interface for policy documents (Template implemented)
   - PolicyRetrieverView - API endpoint for policy retrieval (Planned)

3. **Templates** (In Progress)
   - Document search template (Implemented)
   - Chat interface template (Planned)

4. **Future Components**
   - PolicyRetriever service
   - CitationGenerator service

## Integration Points
- Uses the shared base template from Core app
- Will share rate limiting approach with PaceNoteFoo
- Uses Bootstrap for consistent styling

## Questions
1. What specific policy documents need to be included?
2. Required response format (Markdown/plain text)?
3. Any audit requirements for queries/responses?