---
agent: agent
---

# Code Optimization Process

_Perfection is not when there is nothing more to add, but rather when there is nothing left to take away._

## CRITICAL REQUIREMENT
**Never make code changes without explicit user consent.** Always present your recommendation and wait for approval before implementing any changes.

## Process Overview
Follow this systematic 6-step approach for every optimization:
1. Survey the Codebase
2. Analyze Current State
3. Identify the Next Simplest Change
4. Present Your Recommendation
5. Get Explicit Consent
6. Make the Change

## Step 1: Survey the Codebase
Understand the project structure and identify optimization opportunities:
- Review directory structure
- Use semantic search or grep to find patterns:
  - Repeated code blocks
  - Long functions or files
  - Complex conditionals
  - Duplicate logic across files

## Step 2: Analyze Current State
For each file or component:
- Understand its purpose
- Analyze current implementation
- Identify where it's used
- Note dependencies and side effects

Look for opportunities to:
- Remove unused code
- Offload to existing dependencies
- Consolidate duplicate patterns
- Optimize for runtime environment
- Reduce dependencies

## Step 3: Identify the Next Simplest Change
Choose **ONE** thing to optimize. Consider these categories:
- **Low-hanging fruit**: Simple renames, removing dead code
- **Consolidation**: Merging similar functions or components
- **Extraction**: Breaking apart large functions
- **Simplification**: Replacing complex logic with clearer alternatives
- **Type safety**: Adding or improving type definitions

**Prioritize changes that:**
- Have clear, measurable benefits
- Don't introduce new complexity
- Are easy to verify and test
- Won't break existing functionality

## Step 4: Present Your Recommendation
Format your suggestion as:

```
I found an opportunity:

**File[s]**: `path/to/file.py`, `path/to/another_file.py`

**Current state**: [Brief description of what the code does now]

**Suggestion**: [What you'd like to change in simple English]

**Why**: [Simple explanation of the benefit - e.g., "easier to read", "removes duplication", "clearer intent"]

**Impact**: [Any files or tests that might be affected]
```

Keep explanations simple and focused on practical benefits.

## Step 5: Get Explicit Consent
**Wait for user approval.** The user may:
- Approve the change
- Ask for modifications
- Reject the suggestion
- Want more context

Never proceed without explicit consent.

## Step 6: Make the Change
Once approved:
1. Implement focused, minimal changes
2. Preserve existing functionality
3. Update related tests if needed
4. Verify no errors introduced

After changes, verify with tests, run relevant test commands for the project


## Core Principles
1. **One thing at a time**: Focus on the next simplest improvement
2. **Explain simply**: Use plain language, not jargon
3. **Get consent first**: Never make changes without approval
4. **Preserve functionality**: Don't break what works
5. **Measure impact**: Consider what changes and what stays the same

## When to Stop
Skip an optimization when:
- The "improvement" adds complexity
- The change is risky or uncertain
- The benefit is marginal
- No clear, simple improvements remain

**Remember:** The goal is to make code simpler, not just different.
