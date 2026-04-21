# Voice AI Patient Registration Agent

Voice-based intake agent: a caller dials a **real U.S. number**, has a **natural** (non-IVR) conversation, and registers **standard U.S. patient demographics**. Data is **persisted** and exposed through a **REST API**. On a return call, previously saved data must still be there.

**Live demo (fill in for reviewers)**

| Item | Value |
|------|--------|
| Repository | _GitHub/GitLab URL_ |
| Phone number | _E.164 / dialable U.S._ |
| API base URL | _e.g. `https://your-app.railway.app`_ |

> **Demo only:** Do not use real PHI. This is a technical assessment, not a HIPAA production system.

## Architecture

High-level design: telephony + voice (STT/TTS) → LLM conversation → **HTTP `POST /patients`** on confirmation → database. Details: [ARCHITECTURE.md](./ARCHITECTURE.md), [TECHNICAL_DESIGN.md](./TECHNICAL_DESIGN.md), [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).

## Tech stack and rationale

| Layer | Choice | Why |
|-------|--------|-----|
| Telephony / voice | Vapi | Abstracts STT/TTS/call control quickly; fits a short time box. |
| LLM | Groq (e.g. Llama 3.3) | Fast inference; good for responsive voice turns. |
| API | FastAPI | Typed validation, OpenAPI, clear HTTP semantics. |
| Database | PostgreSQL or SQLite | Postgres for production-shaped deploy; SQLite acceptable for speed/simplicity. |
| Hosting | Railway | Simple deploy + public URL for webhooks and API. |

## Setup

1. Clone the repository.
2. Create a virtual environment; install Python dependencies (see project `requirements.txt` when added).
3. Copy `.env.example` to `.env` and set variables (see below).
4. Run database migrations / init schema (when implemented).
5. Start the API (e.g. `uvicorn app.main:app --host 0.0.0.0 --port 8000`).
6. In Vapi: point the assistant webhook to your public **`/webhook` (or equivalent)** URL; attach a provisioned number.

For production-like local testing without a public URL, use a tunnel (e.g. ngrok) and set that base URL in Vapi. See [DEPLOYMENT.md](./DEPLOYMENT.md).

## Environment variables

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | Groq API for the LLM. |
| `VAPI_API_KEY` | Vapi API (if server calls Vapi). |
| `DATABASE_URL` | SQLAlchemy/async URL for Postgres or SQLite. |
| `PUBLIC_URL` | Public base URL of this API (webhooks, optional links). |

Add any webhook signing or assistant IDs your integration requires; **never commit secrets**.

## REST API

**Response envelope (success):** `{ "data": <payload>, "error": null }`  
**Errors:** appropriate HTTP status with a consistent error shape (e.g. `{ "data": null, "error": { "message": "...", "details": ... } }`).

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/patients` | List patients. Optional filters: `?last_name=`, `?date_of_birth=`, `?phone_number=` |
| `GET` | `/patients/{id}` | One patient by `patient_id` (UUID). |
| `POST` | `/patients` | Create patient; **201** + created record including `patient_id`. |
| `PUT` | `/patients/{id}` | Update patient; **partial** updates allowed. |
| `DELETE` | `/patients/{id}` | **Soft delete:** set `deleted_at`; do not hard-delete. |

Validate all inputs **server-side**; do not rely on the voice agent alone.

## Voice agent ↔ API

On caller **confirmation**, the agent should call **`POST /patients`** (or the same service layer the API uses). Speak back **success** or a **graceful error** if the write fails.

**Bonus:** If the caller’s phone matches an existing patient, offer: _“It looks like we already have a record for [First Name] [Last Name]. Would you like to update your information instead?”_

## Observability

Log at least the **final structured payload** (and/or conversation summary) to **stdout** or a log file for debugging and review.

## Testing the system

1. Call the provisioned number; complete registration with confirmation.
2. `GET /patients` and `GET /patients/{id}` — data matches what was spoken.
3. Restart the server (or redeploy); data must **persist**.
4. Exercise invalid input (e.g. bad DOB) — agent re-prompts; API returns **422**/400 as appropriate.

## Evaluation checklist (self-review)

Aligned with the take-home rubric (each ~20%): **working end-to-end**, **conversational quality** (natural, corrections, confirmation), **architecture** (separation of concerns, schema, REST), **code/docs** (README, prompts, trade-offs), **edge cases** (invalid data, failed DB, dropped call, start over).

## Limitations and trade-offs

Document honestly, e.g.: SQLite vs Postgres; simplified auth; no real HIPAA controls; partial bonus features; known telephony latency. Prefer a **smaller system that works** over a fragile large one.

## Next steps

If time runs out, list unfinished items here (e.g. duplicate-phone flow, tests, dashboard). Partial **working** submissions are better than broken scope creep.

## Related docs

- [FEATURES.md](./FEATURES.md) — scope vs bonuses  
- [USER_STORIES.md](./USER_STORIES.md) — acceptance-style scenarios  
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Railway, Vapi, fallbacks  
- [ITERATION_PLAN.md](./ITERATION_PLAN.md) — build order  
- [PROMPTS.md](./PROMPTS.md) — LLM / agent prompting notes  
