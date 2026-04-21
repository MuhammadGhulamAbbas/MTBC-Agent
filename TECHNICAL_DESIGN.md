# Technical design — voice agent and API

## Conversation phases

1. **Greeting** — intake coordinator tone; explain you will collect registration details.
2. **Required fields** — collect every required field below before treating optional blocks as complete.
3. **Optional bundle offer** — do **not** ask every optional field on every call. After required fields, offer:

   > “I can also collect your insurance information, emergency contact, and preferred language. Would you like to provide any of those?”

   Only ask optional items the caller opts into.
4. **Read-back confirmation** — speak back **all collected fields**; ask the caller to **confirm** or **correct** any field. Loop on corrections until confirmed or caller abandons.
5. **Persist** — on confirmation, call **`POST /patients`** (or shared service). Tell the caller if save **succeeded** or **failed** (no silent failure).
6. **Closing** — brief confirmation (e.g. “You’re all set, [First Name].”) and graceful end.

## Required vs optional fields (API / DB)

**Required:** `first_name`, `last_name`, `date_of_birth`, `sex`, `phone_number`, `address_line_1`, `city`, `state`, `zip_code`  
**Optional:** `email`, `address_line_2`, `insurance_provider`, `insurance_member_id`, `preferred_language` (default English in DB), `emergency_contact_name`, `emergency_contact_phone`  
**Auto:** `patient_id`, `created_at`, `updated_at`; **`deleted_at`** on soft delete only.

## Validation (mirror server-side)

| Field | Rules |
|-------|--------|
| `first_name`, `last_name` | 1–50 chars; letters, hyphens, apostrophes. |
| `date_of_birth` | Valid calendar date; **not in the future**; normalize to stored date (caller may say MM/DD/YYYY). |
| `sex` | One of: `Male`, `Female`, `Other`, `Decline to Answer`. |
| `phone_number` | Valid **U.S. 10-digit** (store normalized; E.164 optional). |
| `email` | Valid email format if present. |
| `address_line_1`, `city` | Required; length caps per schema. |
| `state` | Valid **2-letter U.S. state** abbreviation. |
| `zip_code` | **5-digit** or **ZIP+4** U.S. format. |
| `insurance_member_id` | Alphanumeric if present. |
| `emergency_contact_phone` | 10-digit U.S. if present. |

All of the above must be enforced again in **FastAPI** / Pydantic (or equivalent); the voice layer is not the only gate.

## LLM behavior

- **Natural dialogue** — varied phrasing, clarifying questions, not a rigid script.
- **Corrections** — e.g. spelling last name letter-by-letter; re-integrate corrected slots.
- **Invalid input** — if interpretation fails validation (e.g. 3-digit phone, future DOB), **re-prompt that specific field** with a short reason.
- **Interruptions** — tolerate out-of-order answers where reasonable; re-ask missing slots.

## Errors and resilience

| Situation | Behavior |
|-----------|----------|
| Invalid field | Re-prompt **only** that field until valid or caller quits. |
| API / DB failure after confirmation | Spoken **graceful error**; optionally offer retry or callback note. |
| Duplicate phone (**bonus**) | `GET /patients?phone_number=` (or internal lookup); offer **update** vs new registration. |
| Call drop | Document limitation; optional: partial session cleanup. No phantom saves without confirmation. |
| Start over | If caller asks to restart, reset in-memory/session state; do not POST until a new confirmation. |

## REST integration

- **Success path:** `POST /patients` returns **201** and body under `{ "data": ... }`.
- **Client errors:** **400** / **422** with clear `error` payload; agent should not dump raw JSON to the caller — paraphrase kindly.
- **Soft delete:** `DELETE /patients/{id}` sets `deleted_at`; list endpoints may exclude soft-deleted rows by default.
