# PaceNoteFoo App Specification

## Purpose
Tool for generating pace notes based on user observations and rank.

## Current Implementation
- Bootstrap-styled UI for pace notes generation
- Client-side JavaScript for form handling and response display
- Session storage for preserving user input
- Simulated rate limiting display
- Copy to clipboard functionality

## Planned Features
- Backend API for pace note generation
- RAG implementation for military documentation
- LLM response generation
- Data validation/sanitization
- Server-side rate limiting

## Components
1. **Views**
   - pace_notes_view - Renders the pace notes interface

2. **Templates**
   - pace_notes.html - Bootstrap-styled interface for generating pace notes

3. **Static Files**
   - js/paceNotes.js - Client-side functionality for the pace notes interface
   - css/paceNote.css - Custom styles for the pace notes interface

4. **Future Components**
   - RagRetriever service (Military field manual PDFs?)
   - LLMClient (Integration with chosen LLM provider)
   - API endpoints for pace note generation

## User Flow
1. User enters observations in the text area
2. User selects their rank from the dropdown
3. User clicks "Generate Pace Note" or uses Ctrl+Enter shortcut
4. System displays a loading indicator
5. System generates and displays the pace note
6. User can copy the pace note to clipboard

## Questions
1. What specific data sources should RAG use?
2. Should responses include structured data (tables/formatting)?
3. Any specific safety controls for generated content?
