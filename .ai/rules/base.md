# Copilot Instructions

## Development Philosophy
- **Simplicity**: Keep everything minimal and straightforward
- **Learning Focus**: Prioritize understanding over complexity
- **Iterative Development**: Build features incrementally

## User Interaction
- **Educational Approach**: User is new to Django and Python
- **Instruction Clarification**: Question ambiguous directions
- **Error Correction**: Respectfully identify misconceptions or mistakes
- **Alternatives**: Suggest better approaches when user instructions seem suboptimal
- **Explanations**: Provide context for why certain patterns are recommended
- **Learning Path**: Balance immediate solutions with knowledge building

## Planning Phase
- **Start with Overview**: Begin sessions by sharing `.app_logic/overview.md`
- **Focus Area**: Clearly state which project part we're working on
- **Explicit Preferences**: State implementation preferences upfront
- **Note pad**: use the .cursor/notepad dir to explain and present to the user in longform. 

## Implementation Phase
### Architecture
- Use Django's default structure
- Keep apps focused on single responsibilities
- Place reusable code in core app

### Coding Standards
- **Models**: Descriptive names, `__str__` methods, validators, business logic
- **Views**: Class-based when appropriate, simple, focused, leverage generics
- **Templates**: Inheritance, logic in views, Django template tags
- **Security**: Django's features, no hardcoded secrets, environment variables

### Process
- Start with simple implementations
- Add complexity ONLY when needed
- Note similar existing code when available
- Follow established patterns

## Review Phase
- **Testing**: Placeholder for now. Will build tests later.
- **Documentation**: Brief file overviews at the top, 1-line function docstrings
- **Feedback Loop**: Provide quick feedback on approaches
- **Iterative Clarification**: Ask questions for clarity
- Regularly review and suggest refactoring code
- Document decisions and learnings