# Architecture

## Components

| Layer | Responsibility |
|-------|----------------|
| **Voice** | Vapi: inbound call, STT, TTS, streaming or turn-based audio. |
| **LLM** | Groq (e.g. Llama 3.3): natural dialogue, clarifications, corrections, structured extraction or tool calls. |
| **Backend** | FastAPI: REST API, server-side validation, persistence orchestration, webhooks from Vapi. |
| **Database** | PostgreSQL or SQLite: durable patient records, constraints, indexes. |

## Data flow

```
Caller  ↔  Vapi (telephony + voice)  ↔  LLM (Groq)
                    │
                    ▼
              FastAPI (webhook + REST)
                    │
                    ▼
              Database (patients)
```

1. Caller speaks; Vapi produces text (and optional events).
2. Text (and context) go to the LLM; the agent drives a **conversational** flow (not a fixed IVR tree).
3. When the caller **confirms** the read-back, the backend builds a payload and **persists via the same path as the public API** — ideally **`POST /patients`** or a shared service function invoked by both the HTTP route and the webhook handler.
4. Response text is sent back through Vapi as TTS; include **success or graceful failure** after the database write.

## Rules

- **Database is the source of truth** after a successful commit.
- The LLM **does not** bypass the API layer for writes; keep one validation and persistence path.
- **Logging:** emit at least the final collected payload (or equivalent summary) to **stdout** for observability.

## Separation of concerns (reviewer lens)

- **Telephony / audio:** Vapi configuration, phone number, webhooks.
- **Conversation logic:** prompts, tools, state machine or slot-filling strategy — see [PROMPTS.md](./PROMPTS.md).
- **Data layer:** schema, migrations, queries — see [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md).
- **HTTP API:** REST contracts, status codes, JSON envelope — see [README.md](./README.md).
