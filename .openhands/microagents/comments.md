---
triggers:
- comment
- comments
- commenting
- documentation
- document
- standardize
agent: CodeActAgent
---

# Python Comment Standards

## CRITICAL REQUIREMENT
This repository follows a strict commenting standard for **ALL** `.py` files (except simple `__init__.py` files that only re-export names).

## File-Level Comments (Required)

Every Python module must have a module docstring at the **very top** that:
1. Includes the file path
2. States the responsibility/purpose of the code in the file
3. Lists all top-level functions or classes

### Format:
```python
"""
<file_path>

<Brief description of file's purpose and responsibility>

Top-level declarations:
- <FunctionOrClassName>: <very short description>
- <FunctionOrClassName>: <very short description>
- ...
"""
```

### Example:
```python
"""
src/utils/env_utils.py

Environment utilities helpers that centralize the runtime configuration helpers.

Top-level declarations:
- is_dev_mode: Check if the environment is configured for development
"""
```

## Function/Class Comments (Required)

Every top-level function or class must have a docstring immediately after its definition that:
1. Expands on the short description from the module docstring
2. Provides additional context about its purpose or behavior

### Format:
```python
def my_function():
    # More detailed description expanding on the reference from file header
    ...
```

### Important Notes:
- **ALWAYS** use docstrings (triple quotes) for top of file comments
- **NEVER** rely solely on inline comments to describe public APIs
- Docstring should be descriptive but concise
- Docstring should add value beyond what the function name provides

## Inline Comments (Minimal)

Minimize inline comments within functions. **Only add them when:**
1. Documenting a specific lesson learned
2. Explaining a non-obvious solution to a specific problem
3. Noting a workaround for a known issue

**Avoid:**
- Obvious comments that just restate what the code does
- Redundant comments that explain self-documenting code
- Excessive comments that clutter the code
