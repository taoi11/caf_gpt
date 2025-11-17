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

# TypeScript Comment Standards

## CRITICAL REQUIREMENT
This repository follows a strict commenting standard for **ALL** `.ts` files (except simple `index.ts` files that only contain imports/exports).

## File-Level Comments (Required)

Every TypeScript file must have a multi-line comment at the **very top** that:
1. Includes the file path
2. States the responsibility/purpose of the code in the file
3. Lists all top-level functions or classes

### Format:
```typescript
/**
 * <file_path>
 *
 * <Brief description of file's purpose and responsibility>
 *
 * Top-level declarations:
 * - <FunctionOrClassName> : <very short description>
 * - <FunctionOrClassName>: <very short description>
 * ...
 */
```

### Example:
```typescript
/**
 * src/utils/EnvUtils.ts
 *
 * Environment utilities
 *
 * Top-level declarations:
 * - isDevMode: Check if environment is in development mode
 */

// Check if environment is in development mode
export function isDevMode(env: Env): boolean {
  return env.DEV !== "false";
}
```

## Function/Class Comments (Required)

Every top-level function or class must have a **single-line comment** immediately before it that:
1. Expands on the short description from the file header
2. Provides additional context about its purpose

### Format:
```typescript
// <More detailed description expanding on the reference from file header>
export class MyClass {
  // ...
}

// <More detailed description expanding on the reference from file header>
export function myFunction() {
  // ...
}
```

### Important Notes:
- **ALWAYS** use single-line `//` format
- **NEVER** use multi-line `/* */` format for function/class comments
- Comment should be descriptive but concise
- Comment should add value beyond what the function name provides

## Inline Comments (Minimal)

Minimize inline comments within functions. **Only add them when:**
1. Documenting a specific lesson learned
2. Explaining a non-obvious solution to a specific problem
3. Noting a workaround for a known issue

**Avoid:**
- Obvious comments that just restate what the code does
- Redundant comments that explain self-documenting code
- Excessive comments that clutter the code
