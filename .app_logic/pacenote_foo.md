# PaceNote App Implementation

## Purpose
Tool for generating professional feedback notes based on user observations and rank, using LLM models.

## Current Implementation
- Django-based web application with a simple, focused interface
- Integration with Open Router API for LLM access (using Claude 3.5 Haiku)
- System prompt templates stored in the application
- Rank-specific competency lists (starting with Cpl/MCpl)
- Examples stored in S3 bucket for reference
- Simple workflow: user inputs description → selects rank → system generates feedback note
- Simulated rate limiting display
- Copy to clipboard functionality

## Components

### 1. Django App Structure
- `pacenote_foo/` - Main application directory
  - `views.py` - Views for handling pace note generation
  - `urls.py` - URL routing
  - `models.py` - Data models (placeholder for future use)
  - `services/` - Service modules for API integration
  - `prompts/` - Prompt templates

### 2. Core Services
- `core/services/open_router_service.py` - Open Router API integration
- `core/utils/s3_client.py` - S3 bucket access
- `pacenote_foo/services/prompt_service.py` - Prompt template handling

### 3. Templates and Static Files
- Using existing project templates and static files:
  - `templates/pace_notes.html` - Bootstrap-styled interface
  - `static/js/paceNotes.js` - Client-side functionality
  - `static/css/paceNote.css` - Custom styles

### 4. External Resources
- System prompt template (from `pacenote_foo/prompts/base.md`)
- Competency lists for Cpl/MCpl rank (from S3: `paceNote/cpl_mcpl.md`)
- Examples (from S3: `paceNote/examples.md`)

## User Flow
1. User navigates to the PaceNote web page (`/pacenote_foo/`)
2. User enters a brief description of events in the text area
3. User selects their rank from the dropdown (currently only Cpl/MCpl available)
4. User clicks "Generate Pace Note" or uses Ctrl+Enter shortcut
5. System displays a loading indicator
6. System retrieves appropriate competency list and examples from S3
7. System constructs prompt with user input, competency list, and examples
8. System sends prompt to Open Router API and receives generated feedback note
9. System displays the formatted feedback note to the user
10. User can copy the feedback note to clipboard

## Technical Implementation Details

### Views
- `PaceNoteView` - Renders the pace notes interface
- `PaceNoteGeneratorView` - API endpoint for generating pace notes

### Services
- **OpenRouterService**:
  - Implemented in `core/services/open_router_service.py`
  - Uses the "anthropic/claude-3.5-haiku:beta" model
  - Provides a simple interface for sending prompts and receiving completions
  - Includes error handling and logging

- **S3Client**:
  - Uses the existing `core/utils/s3_client.py`
  - Configured to access the "policies" bucket
  - Retrieves competency lists and examples from S3

- **PromptService**:
  - Implemented in `pacenote_foo/services/prompt_service.py`
  - Loads the base prompt template from the filesystem
  - Constructs prompts by replacing variables with content

### API Endpoints
- `/pacenote_foo/api/generate-pace-note/` - POST endpoint for generating pace notes
  - Accepts JSON with `user_input` and `rank` fields
  - Returns JSON with `status` and `pace_note` fields

### Frontend Integration
- Updated `static/js/paceNotes.js` to call our API endpoint
- Implemented error handling and loading states
- Maintained existing UI for consistency

## Future Enhancements
- Add caching for S3 resources to improve performance
- Implement actual rate limiting
- Add more rank options with corresponding competency lists
- Enhance error handling and logging
- Add analytics for tracking usage patterns
- Implement the `PaceNote` model to store generated notes for reference

## Environment Configuration
The following environment variables are required:
- `OPENROUTER_API_KEY` - API key for Open Router
- `AWS_ACCESS_KEY_ID` - Access key for S3
- `AWS_SECRET_ACCESS_KEY` - Secret key for S3
- `AWS_S3_ENDPOINT_URL` - S3 endpoint URL (https://gateway.storjshare.io)
