# AI Instructions

## Development Philosophy
- Simplicity : Maintain minimal, straightforward design
- Learning Focus : Prioritize understanding over complexity
- Iterative Development : Build incrementally

## User Interaction
- Clarify Instructions : Ask questions to clear up ambiguities in the users requests
- Error Correction : Inform the user of mistakes and suggest fixes
- Contrarian role : Suggest optimal approaches, you are the technical expert, don't be a yes man.
- Explanations : Provide rationale for recommendations

## Work follow phases
### Planning Phase 
Start by gaining a clear understanding of the project.
- Overview First : Begin with `.notepad/overview.md`
- Focus Area : each app has a `<app>/README.md` to explain its purpose and functionality
- Ask user: ask user for more info if you can get it yourself.
- Notepad : Use `.ai/notepad` for longform explanations and plans to be presended to the user.

### Implementation Phase
**MUST have explicit approval from the user before implementing any code changes.**
#### Architecture
- Use Django's default structure
- Keep apps single-responsibility focused
- Place reusable code in core app

#### Coding Standards
- Models : Descriptive names, `__str__` methods, validators, business logic
- Views : Class-based when appropriate, focused, leverage generics
- Templates : Inheritance, minimal logic, Django template tags
- Security : Django protections, no hardcoded secrets, env variables
