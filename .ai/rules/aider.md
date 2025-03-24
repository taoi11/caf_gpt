# Aider: CLI AI Coding Assistant

## Purpose
- Cost-effective (5x cheaper than Claude) for routine tasks
- Edits files per prompt.md instructions
- Two-pass: implementation then self-review

## Best For
- Docstrings, type annotations, error handling, formatting, refactoring, cleanup

## Usage
1. Update or create prompt.md with detailed instructions
2. Configure `./aider.sh` with:
   - `--read` for context files
   - `--file` for target files
3. User will execute `./aider.sh`
4. User will give you output as commits
