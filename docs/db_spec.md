# Database Specification

## Overview

CAF-GPT uses Neon (serverless Postgres) to store user memory - a living prose narrative that captures interaction patterns and preferences. This memory is injected into agent system prompts to provide personalized context.

## Provider

- **Neon** <https://neon.tech> - Serverless Postgres
- Connection via `psycopg2` (sync) with connection string from environment
- Matches existing sync architecture (no async/await)

## Schema

### users

Stores hashed user identifiers. Users are identified by the username portion of their email (before the `@`), allowing `john.smith@forces.gc.ca` and `john.smith@ecn.forces.gc.ca` to resolve to the same user.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA-256 of lowercase username
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email_hash ON users(email_hash);
```

**Hashing strategy:**
```python
import hashlib

def hash_email(email: str) -> str:
    """Extract username from email and hash it."""
    username = email.lower().split("@")[0]
    return hashlib.sha256(username.encode()).hexdigest()
```

### memory

Stores the living prose narrative per user. One row per user, updated after every email interaction.

```sql
CREATE TABLE memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL DEFAULT '',  -- Prose narrative (3-5 paragraphs)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT unique_user_memory UNIQUE (user_id)
);

CREATE INDEX idx_memory_user_id ON memory(user_id);
```

## Memory Structure

The memory content is a prose narrative (not structured JSON), similar to Claude.ai's memory feature. It should be 3-5 paragraphs covering:

```text
Work context
Brief professional background - rank, general trade/occupation, areas of expertise
relevant to their questions. No specific unit or posting location.

Interaction patterns
How the user typically engages with CAF-GPT. Which agent they use most (policy
vs pacenote), common question topics, communication style preferences.

Top of mind
Current focus areas based on recent interactions. What they're actively working
on or asking about. This section is the most dynamic.

History
Longer-term patterns observed over time. How their usage has evolved, recurring
themes across many interactions.
```

## Memory Agent

A dedicated agent that runs after every successful email reply to update the user's memory.

**Trigger:** After `AgentCoordinator` returns a successful reply and email is sent

**Input:**
- Current memory (or empty string for new users)
- The email exchange just completed (user's email + agent's reply)

**Output:**
- Updated memory text

**Behavior:**
- Synthesizes new information into existing narrative
- Maintains the 3-5 paragraph structure
- Follows privacy rules strictly
- If nothing new worth remembering, returns memory unchanged

## Privacy Rules

The memory agent MUST follow these rules:

### ALLOWED

| Category | Example |
|----------|---------|
| General role | "The user is a Corporal in a combat engineer trade" |
| Interaction patterns | "Frequently asks about leave policy" |
| Preferences | "Prefers concise, direct answers" |
| Op names + high-level | "Participated in Op REASSURANCE" |
| Agent preferences | "Primarily uses the pacenote agent for MCpl feedback notes" |

### NOT ALLOWED

| Category | Example (DO NOT STORE) |
|----------|------------------------|
| Names | Use "the user", "a peer", "a colleague" instead |
| Service numbers | Any SN format (e.g., A12 345 678) |
| Specific dates | "Going on leave March 15th" |
| Unit/location | "Posted to 1 CER Edmonton" |
| Detailed op info | Specific roles, dates, locations within operations |

## Integration with Agents

Memory is injected into the system prompt for both `prime_foo` and `pacenote` agents:

```python
# In agent coordinator or prompt construction
system_prompt = f"""{base_agent_prompt}

<memory>
{user_memory_content}
</memory>
"""
```

When memory is empty (new user), the `<memory>` block is omitted or contains a note like "No prior interaction history."

## Data Flow

```text
1. Email received
2. Extract sender email, hash username → email_hash
3. Look up user by email_hash (create if not exists)
4. Fetch user's memory
5. Inject memory into agent system prompt
6. Agent processes email, generates reply
7. Reply sent successfully
8. Memory agent runs:
   - Input: current memory + email exchange
   - Output: updated memory
9. Save updated memory to database
```

## Environment Configuration

```bash
# .env additions
DATABASE__URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

```python
# src/config.py addition
class DatabaseConfig(BaseSettings):
    url: str

    model_config = SettingsConfigDict(env_prefix="DATABASE__", extra="ignore")
```

## Future Considerations

These are NOT part of the initial implementation but noted for future expansion:

- **Interaction logs**: Store email metadata (timestamp, agent used, success/fail) for analytics
- **Memory versioning**: Track memory changes over time
- **Memory search**: If memory grows large, semantic search for relevant sections
- **Per-project memory**: Separate memory contexts (similar to Claude.ai projects)
- **Admin dashboard**: View/edit memories, usage stats
