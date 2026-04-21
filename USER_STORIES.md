# User stories and acceptance notes

## Registration — happy path

**As a** caller  
**I want** to register my demographics by speaking naturally  
**So that** my information is stored without filling a paper form.

**Acceptance**

- Agent greets and collects **all required** fields conversationally.
- After required fields, agent offers **optional** bundle (insurance, emergency contact, preferred language) per spec; caller can decline.
- Agent **reads back** everything collected; I can **confirm** or **correct** any field.
- On confirm, backend **persists** via `POST /patients` (or shared service).
- I hear a **short success** closing (e.g. “You’re all set, [First Name].”).
- `GET /patients` / `GET /patients/{id}` returns the saved record with correct fields.

## Persistence

**As a** reviewer  
**I want** data to survive a **second call** and server restarts  
**So that** I can verify durability.

**Acceptance**

- After Call 1 registers “Jane Doe”, Call 2 (or API query) still finds the record (unless soft-deleted).

## API consumption

**As an** integrator  
**I want** predictable REST behavior  
**So that** I can list, read, create, update, and soft-delete patients.

**Acceptance**

- Filters on list endpoint work as documented.
- `PUT` accepts partial body; validation errors return **422** with clear errors.
- `DELETE` sets `deleted_at` only; record not physically removed.

## Invalid input

**As a** caller  
**I want** the agent to **fix mistakes** without starting over  
**So that** bad dates or phone numbers are corrected easily.

**Acceptance**

- Future DOB, malformed phone, invalid state/ZIP → agent **re-asks that field** specifically.
- API rejects the same bad payloads with appropriate HTTP errors.

## Failure handling

**As a** caller  
**I want** to know if saving failed  
**So that** I am not told “you’re done” when nothing was stored.

**Acceptance**

- If `POST /patients` fails, I hear a **graceful** explanation, not silence or raw JSON.

## Duplicate phone (bonus)

**As a** returning caller  
**I want** the system to recognize my number  
**So that** I can **update** instead of creating a duplicate.

**Acceptance**

- Agent offers update path using existing name; flow leads to `PUT` or appropriate API path.

## Security and demo data (non-functional)

**As a** reviewer  
**I expect** no secrets in source and **demo-only** data  
**So that** the submission matches assessment constraints.

**Acceptance**

- Keys only in environment variables; README states **no real PHI**.
