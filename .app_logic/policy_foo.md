# PolicyFoo App Specification

## Purpose
LLM workflow for answering policy/regulation questions

## Key Features
- Rate-limited chat interface with reference citations
- RAG over policy documents
- Response validation against sources
- Export capability for answers

## Components
1. **Views**
   - ChatInterfaceView (rate limited)
   - DocumentSearchView
2. **Services**
   - PolicyRetriever (What document formats?)
   - CitationGenerator
3. **Models**
   - DocumentSource (If storing references)

## Questions
1. What specific policy documents need to be included?
2. Required response format (Markdown/plain text)?
3. Any audit requirements for queries/responses?