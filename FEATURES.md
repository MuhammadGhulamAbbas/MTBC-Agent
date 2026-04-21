# Features — scope vs assessment PDF

Legend: **MVP** = core take-home | **Bonus** = optional depth

## Telephony and voice agent (MVP)

- [ ] Real, dialable **U.S. phone number** (e.g. Vapi + provider)
- [ ] **Conversational** flow (not rigid IVR)
- [ ] **LLM-powered** understanding, clarifications, corrections
- [ ] **Read-back confirmation** before save
- [ ] **Invalid data** → re-prompt that field
- [ ] **Graceful call ending** after success

## Data model and database (MVP)

- [ ] All PDF fields + constraints; persistence survives **restart**
- [ ] Schema enforces types and rules (see [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md))
- [ ] Optional: **1–2 seed patients** for demos

## REST API (MVP)

- [ ] `GET /patients` with optional `last_name`, `date_of_birth`, `phone_number`
- [ ] `GET /patients/:id` by UUID
- [ ] `POST /patients` create (**201**, full record in `data`)
- [ ] `PUT /patients/:id` partial update
- [ ] `DELETE /patients/:id` **soft delete** (`deleted_at`)
- [ ] Status codes: 200, 201, 400, 404, 422, 500 as appropriate
- [ ] JSON envelope: `{ "data": ..., "error": null }` (and error shape on failure)
- [ ] **Server-side validation** on every mutating route

## Voice ↔ persistence (MVP)

- [ ] On caller confirm: **`POST /patients`** (or same service layer)
- [ ] Caller hears **success** or **spoken error** if write fails

## Bonus (PDF + extras)

- [ ] **Duplicate detection** by phone → offer update existing patient
- [ ] Appointment scheduling (mock)
- [ ] **Multi-language** (e.g. switch to Spanish)
- [ ] Call **transcript** / summary stored with patient
- [ ] Simple **web dashboard** listing patients
- [ ] **Automated tests** for API

## Implementation status

Update the line below as you build:

**Status:** _planned → in progress → done_
