# CAF GPT — AI agent quickstart

This is a Django monolith with three apps: `core` (infra/services), `pacenote_foo` (note generation), and `policy_foo` (policy Q&A). Use these conventions to be productive fast.

## Architecture and data flow
- Settings switcher: `caf_gpt/settings/__init__.py` maps `DJANGO_ENV` to `dev.py` or `prod.py`. Root module is `caf_gpt.settings`.
- URLs: `caf_gpt/urls.py` mounts `core`, `pacenote_foo`, `policy_foo`, and `csp-report/`.
- Services live in `core/services/*`; views are thin and call services. Cost is tracked globally via `core.services.cost_tracker_service.cost_context` in templates.
- Unmanaged data models: `core.models.DoadDocument` (table: `doad`) and `LeaveDocument` (table: `leave_2025`) read content from an external Postgres. `CostTracker` (table: `cost_tracker`) is managed and stores a single running total.

## Key flows
- PaceNote: POST /pacenote/api/generate-pace-note/ → `validate_turnstile_token` → `pacenote_foo/services.generate_pace_note()` → reads local prompts in `pacenote_foo/prompts/**` → `OpenRouterService(model=...)` → returns pace_note string and triggers background cost tracking.
- Policy chat: POST /policy/api/chat/ → `validate_turnstile_token` → `policy_foo/views/router.PolicyRouterView` routes by `policy_set` (currently `doad`) → calls `views/doad_foo/handle_doad_request` (orchestrates finder/reader/synthesizer) → returns `assistant_message`.

## Conventions that matter
- Always include Cloudflare Turnstile: both PaceNote and Policy endpoints require `turnstile_token`. Site key is injected into templates as `turnstile_site_key`.
- Explicit LLM model required: `OpenRouterService(model=...)` (e.g., `openai/gpt-4.1`). Pass messages as OpenAI-style `[{'role','content'}]`.
- Cost tracking: `OpenRouterService` reads `result.id` and `CostTrackerService` updates `cost_tracker.total_usage` asynchronously. Ensure table `cost_tracker` exists with a row id=1.
- CSP is enforced (`django-csp`); report endpoint is `/csp-report/`. External assets are blocked by default (fonts/images); update settings if you add CDNs.
 - Prompt files are read-only: all `*.md` under `pacenote_foo/prompts/**` (and any prompt `.md` elsewhere) must not be modified by AI agents — only the user can edit these. Treat them as immutable inputs.

## How to run and debug
For local development set environment variables (e.g., `DJANGO_ENV=development`, `DATABASE_URL=postgres://...`, `OPENROUTER_API_KEY=...`) and run `python manage.py runserver` (admin/debug toolbar only loads when `DEBUG=True`); verify DB connectivity and sample DOAD data with `python manage.py test_database`; for containers use `docker compose up --build` (production uses Gunicorn + WhiteNoise and static files are collected to `staticfiles/` in the image). 
Linting: Use the `lint` command (available in nix-shell) which auto-fixes formatting with `autopep8` then runs `flake8`; alternatively run `python -m flake8` or `flake8` directly. Flake8 is configured via `.flake8` (max-line-length=200; ignores common build/asset dirs; selects E,F,W,C90,B,S; extends-ignore=E261; max-complexity=10).

## Request payloads (examples)
- PaceNote POST /pacenote/api/generate-pace-note/
  { "user_input": "text...", "rank": "sgt", "turnstile_token": "..." }
  Response: { "status": "success", "pace_note": "..." } or { "status":"error","message":"..." }
- Policy chat POST /policy/api/chat/
  { "messages": [
    {"role":"user","content":"Initial question form the user... >"},
    {"role":"assistant","content":"Initial response..."},
    {"role":"user","content":"Follow-up question from the user... >"}
  ], "policy_set": "doad", "turnstile_token": "..." }
  Response: { "assistant_message": "..." }

## Extending safely
- New policy set: add `policy_foo/views/<set>/**` with a `handle_<set>_request(messages)` entry point; add `<set>` to `supported_policy_sets` in `router.PolicyRouterView` and import it for routing.
- New prompts for PaceNote: add files under `pacenote_foo/prompts/competencies/` and reference via `rank` value; `local_file_reader` handles lookup and errors.

## Pointers to important files
- Settings: `caf_gpt/settings/{base,dev,prod}.py` and `__init__.py`
- URLs: `caf_gpt/urls.py`, `pacenote_foo/urls.py`, `policy_foo/urls.py`
- Services: `core/services/open_router_service.py`, `core/services/cost_tracker_service.py`, `core/services/turnstile_service.py`
- Turnstile utils: `core/utils/turnstile_utils.py`
- Data models: `core/models.py`

Notes
- Unmanaged tables `doad` and `leave_2025` already exist in the database.
