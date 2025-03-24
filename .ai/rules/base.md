# Copilot Instructions

## Development Philosophy
- **Simplicity**: Maintain minimal, straightforward design
- **Learning Focus**: Prioritize understanding over complexity
- **Iterative Development**: Build incrementally

## User Interaction
- **Clarify Instructions**: Ask question to clear up ambiguities
- **Error Correction**: Inform the user of mistakes and suggest fixes
- **Alternatives**: Suggest optimal approaches, you are the technical expert
- **Explanations**: Provide rationale for recommendations

## Planning Phase
- **Overview First**: Begin with `.app_logic/overview.md`
- **Focus Area**: Specify current project component
- **Explicit Preferences**: State implementation choices upfront
- **Notepad**: Use `.cursor/notepad` for longform explanations

## Implementation Phase
### Architecture
- Use Django's default structure
- Keep apps single-responsibility focused
- Place reusable code in core app

### Coding Standards
- **Models**: Descriptive names, `__str__` methods, validators, business logic
- **Views**: Class-based when appropriate, focused, leverage generics
- **Templates**: Inheritance, minimal logic, Django template tags
- **Security**: Django protections, no hardcoded secrets, env variables

### Process
- Start simple
- Add complexity ONLY when necessary
- Reference similar existing code
- Follow established patterns

## Review Phase
- **Testing**: Implement later, Placeholder
- **Code Level Documentation**: Brief file headers, concise function docstrings
- **Clarification**: Ask targeted questions
- Review code regularly, suggest refactoring, do not action without approval
- Document decisions and learnings in .ai/notepad/ dir