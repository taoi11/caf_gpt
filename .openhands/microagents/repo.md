# OpenHands Instructions

## Development Philosophy
- Simplicity : Maintain minimal, straightforward design
- Learning Focus : Prioritize understanding over complexity
- Iterative Development : Build incrementally

## Project Structure
`.ai/` : Contains notes and rules for AI assistants
- Focus Area :
  - the main `README.md` contains the overview and structure of the project
  - each app has a `<app>/README.md` to explain its purpose and functionality
- Notepad : Use `.ai/notepad` for longer notes, ideas and docs for external tools used in the project

#### Architecture
- Use Django's default structure
- Place reusable code in core app

#### Coding Standards
- Models : Descriptive names, `__str__` methods, validators, business logic
- Views : Class-based when appropriate, focused, leverage generics
- Templates : Inheritance, minimal logic, Django template tags
- Security : Django protections, no hardcoded secrets, env variables
