# PaceNote App

## Purpose
Generate professional feedback notes for CAF members based on user observations and rank-specific competencies.

## App-Specific Components

### Views
- **PaceNoteView**: Main interface for pace note generation
  - Renders the interactive form interface
  - Handles GET requests for the main page
- **PaceNoteGeneratorView**: API endpoint handling LLM requests
  - Input validation and sanitization
  - Rate limiting integration via RateLimitService
  - Error handling with appropriate status codes
  - Integration with OpenRouterService for LLM generation

### Services
- **PromptService**: Template management and variable substitution
  - Loads base prompt template
  - Inserts rank-specific competencies from S3
  - Formats messages for LLM API
  - Handles error cases for missing resources
  - Caches templates for performance

### Templates & Static Files
- **pace_notes.html**: Interactive form interface
  - Rank selection dropdown
  - Text input area for observations
  - Generation button and loading indicators
- **paceNotes.js**: AJAX handling and UI interactions
  - Form submission and response handling
  - Error state management
  - Copy to clipboard functionality
  - Session storage for form persistence
- **paceNote.css**: Custom styling for the interface

### Models (Placeholder)
- **PaceNote**: Model for storing generated notes (future use)

### External Resources
- **S3 Stored Data**:
  - Rank-specific competency lists (cpl.md, mcpl.md, sgt.md, wo.md)
  - Example pace notes (examples.md)
- **Prompt Template**:
  - base.md with competency and example variables

## Feature Details

### Rank Selection
- Four rank levels: Cpl, MCpl, Sgt, WO
- Each with specific competency expectations
- Templates tailored to rank requirements

### Output Format
- Two-paragraph structured feedback
- First paragraph: Description of events (2-3 sentences)
- Second paragraph: Outcomes/impact (2-3 sentences)

### UI Features
- Session storage for input preservation
- Copy to clipboard functionality
- Visual feedback during generation
- Error handling with user-friendly messages
- Mobile-responsive design

## Usage Example

### API Integration
```python
# Generate a pace note via the API
import requests

response = requests.post(
    "/pacenote/api/generate-pace-note/",
    json={
        "user_input": "Member demonstrated excellent leadership during exercise...",
        "rank": "sgt"
    }
)

if response.status_code == 200:
    data = response.json()
    print(data['pace_note'])
else:
    print(f"Error: {response.status_code}")
    print(response.json().get('error', 'Unknown error'))
```
