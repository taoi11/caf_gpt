#!/bin/bash

PROMPT=$(<"prompt.md")

# Aider first run
aider \
  --message "$PROMPT" \
  --auto-commits \
  --no-detect-urls \
  --read ".app_logic/overview.md" \
  --read ".app_logic/core.md" \
  --file "caf_gpt/file_1.py"\
  --file "caf_gpt/file_2.py"\
  --yes

# Aider second run
aider \
  --message "Double check and IF needed (not looking for perfection) fix the work of a code agent that was given the following instructions: $PROMPT" \
  --auto-commits \
  --no-detect-urls \
  --read ".app_logic/overview.md" \
  --read ".app_logic/core.md" \
  --file "caf_gpt/file_1.py"\
  --file "caf_gpt/file_2.py"\
  --yes