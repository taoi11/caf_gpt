# PaceNote App

## Purpose
Generate professional feedback notes for CAF members based on user observations and rank-specific competencies.

## App-Specific Components

### Views
- **PaceNoteView**: Main interface for pace note generation
- **PaceNoteGeneratorView**: API endpoint handling LLM requests

### Services
- **PromptService**: Template management and variable substitution
  - Loads base prompt template
  - Inserts rank-specific competencies
  - Formats messages for LLM API

### Templates & Static Files
- **pace_notes.html**: Interactive form interface
- **paceNotes.js**: AJAX handling and UI interactions
- **paceNote.css**: Custom styling

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
- Simulated rate limiting

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
```

## Implementation Notes
- No database storage currently implemented
- Uses S3 for competency lists and examples
- Model included as placeholder for future enhancements
