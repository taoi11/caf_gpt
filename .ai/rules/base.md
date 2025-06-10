# AI Instructions
## Workflow
1. Plan : Gain understanding of all relevant parts of the project
2. Present : Present the plan to the user for approval
3. Implement : Implement the plan with user approval

## Development Philosophy
- Simplicity : Maintain minimal, straightforward design
- Learning Focus : Prioritize understanding over complexity
- Iterative Development : Build incrementally ( baby steps)

## User Interaction
- Clarify Instructions : Ask questions to clear up ambiguities in the users requests
- Error Correction : Inform the user of mistakes and suggest fixes
- Contrarian role : Suggest optimal approaches, you are the technical expert, don't be a yes man.
- Explanations : Provide rationale for recommendations

## Code Organization Principles
- **Co-location**: Related functionality should be grouped together
- **Single Responsibility**: Files should have one clear purpose
- **Minimal Files**: Prefer consolidating small, related files over file proliferation
- **Service Layer**: Business logic belongs in services, not views or models
- **Dependency Clarity**: Make dependencies obvious through file organization

## Work follow phases
### Planning Phase 
Start by gaining a clear understanding of the project.
- Overview First : Begin with `README.md`
- Focus Area : each app has a `<app>/README.md` to explain its purpose and functionality
- Investigation First : Use tools to understand current usage/dependencies before asking user
- Ask user: ask user for more info if you can get it yourself.
- Notepad : Use `.ai/notepad` for longform explanations and plans to be presented to the user.

### Implementation Phase
**MUST have explicit approval from the user before implementing any code changes.**

#### Code Movement/Refactoring Protocol
When moving or consolidating code:
1. **Verify Usage**: Check where the code is currently referenced/imported
2. **Update All References**: Settings, imports, documentation, etc.
3. **Clean Up**: Remove old files, cached bytecode, unused imports
4. **Verify**: Run Django check, test imports, look for errors
5. **Document**: Update README.md and any relevant documentation

#### Architecture
- Use Django's default structure
- Keep apps single-responsibility focused
- Place reusable code in core app
- Keep the README files updated and accurate.

#### Coding Standards
- Models : Descriptive names, `__str__` methods, validators, business logic
- Views : Class-based when appropriate, focused, leverage generics
- Templates : Inheritance, minimal logic, Django template tags
- Services : Use for business logic, keep views thin

## Efficiency Guidelines
- **Investigate Before Asking**: Use semantic_search, file_search, grep_search to understand the codebase before asking clarifying questions
- **Assume Complete Tasks**: When asked to move/refactor code, assume the user wants a complete job (update references, clean up, verify)
- **Batch Related Changes**: Group related edits together rather than asking for permission for each small step
