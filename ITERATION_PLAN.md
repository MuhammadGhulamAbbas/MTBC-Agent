# Iteration plan (end-to-end first)

Order optimized for a **working vertical slice** before polish — matches “partial working beats broken ambitious.”

## Phase 1 — Data and API core

1. **Database schema** — `patients` table with PDF fields, constraints, `deleted_at`, indexes ([DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)).
2. **FastAPI app** — health route, DB session wiring.
3. **CRUD + list filters** — `GET /patients`, `GET /patients/{id}`, `POST`, `PUT`, soft `DELETE`; JSON envelope; Pydantic validation.
4. **Seed data** (optional) — 1–2 demo rows for API testing.

## Phase 2 — Voice integration

5. **Webhook handler** — receive Vapi events; map to internal session/state.
6. **LLM integration** — Groq; prompt + tools or structured extraction ([PROMPTS.md](./PROMPTS.md)).
7. **Conversation flow** — required → optional offer → read-back → confirm → **`POST /patients`**; spoken success/failure.
8. **Logging** — final payload / summary to stdout.

## Phase 3 — Hardening and deploy

9. **Edge cases** — invalid DOB/phone/state/ZIP; API 422 vs agent re-prompt; DB errors to caller.
10. **Bonus** (time permitting) — duplicate phone → update offer; tests; dashboard; transcript.
11. **Railway** — env vars, Postgres or SQLite strategy, public URL; Vapi webhook + number ([DEPLOYMENT.md](./DEPLOYMENT.md)).
12. **README** — fill live **phone** and **API base URL**; limitations and next steps.

## Phase 4 — Review pass

13. Self-check against rubric in [README.md](./README.md).
14. Dry-run call + API + restart persistence before submission.
