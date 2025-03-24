# Aider: CLI AI Coding Assistant

## Purpose
- Cost-effective (5x cheaper than Claude) for routine code tasks
- Directly edits files based on instructions in prompt.md
- Two-pass system: implementation + self-review

## Best For
- Docstring improvements
- Type annotation additions
- Error handling standardization
- Formatting and refactoring
- Code cleanup tasks

## Usage
1. **Update prompt.md** with specific, step-by-step, detailed instructions
2. **Modify aider.sh** to set:
   - `--read` flags for context files
   - `--file` flags for target files
3. **Running**  the user will execute `./aider.sh` script for you
4. **Review** the user will give you the commits Aider creates to review

## Avoid Using For
- Complex architectural decisions
- Novel feature implementation
