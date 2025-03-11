# PaceNoteFoo App Specification

## Purpose
LLM workflow for generating pace notes from operational data

## Key Features
- Rate-limited chat interface without conversation history
- RAG implementation for military documentation
- LLM response generation
- Data validation/sanitization

## Components
1. **Views**
   - ChatInterfaceView (rate limited)
   - RagSearchView (API)
2. **Services**
   - RagRetriever (Military field manual PDFs?)
   - LLMClient (Integration with ???)
3. **Models**
   - ChatSession (Ephemeral if no storage needed)

## Questions
1. What specific data sources should RAG use?
2. Should responses include structured data (tables/formatting)?
3. Any specific safety controls for generated content?
