# Database schema — `patients`

Aligned with the take-home **Patient Demographic Data Model**. Use DB-level constraints where practical; full rules also enforced in the API layer.

## Table: `patients`

| Column | Type | Nullable | Notes |
|--------|------|----------|--------|
| `patient_id` | UUID | no | Primary key; default `gen_random_uuid()` or app-generated. |
| `first_name` | VARCHAR(50) | no | Letters, hyphens, apostrophes only (check in app / optional CHECK). |
| `last_name` | VARCHAR(50) | no | Same as above. |
| `date_of_birth` | DATE | no | Not in future; no invalid dates. |
| `sex` | VARCHAR / ENUM | no | `Male`, `Female`, `Other`, `Decline to Answer`. |
| `phone_number` | VARCHAR | no | **Unique**; normalized 10-digit US (or E.164 + unique constraint). |
| `email` | VARCHAR | yes | Valid email format if set. |
| `address_line_1` | VARCHAR | no | Street address. |
| `address_line_2` | VARCHAR | yes | Apt / suite / unit. |
| `city` | VARCHAR(100) | no | |
| `state` | CHAR(2) | no | U.S. state abbreviation. |
| `zip_code` | VARCHAR | no | 5-digit or ZIP+4 (validate in app). |
| `insurance_provider` | VARCHAR | yes | |
| `insurance_member_id` | VARCHAR | yes | Alphanumeric if present. |
| `preferred_language` | VARCHAR | yes | Default **English** at insert if omitted. |
| `emergency_contact_name` | VARCHAR | yes | |
| `emergency_contact_phone` | VARCHAR | yes | 10-digit US if present. |
| `created_at` | TIMESTAMPTZ | no | UTC, auto on insert. |
| `updated_at` | TIMESTAMPTZ | no | UTC, auto on update. |
| `deleted_at` | TIMESTAMPTZ | yes | **Soft delete** only; `DELETE /patients/:id` sets this. |

## Indexes

- `phone_number` — unique lookup; supports duplicate-detection bonus.
- `last_name` — list filter `?last_name=`.
- Consider composite or additional indexes if you filter heavily on `date_of_birth` + `last_name`.

## API alignment

- **List:** `GET /patients?last_name=&date_of_birth=&phone_number=`
- **Soft delete:** rows with `deleted_at IS NOT NULL` excluded from default list/read, or returned only when explicitly requested (document behavior in OpenAPI).

## Seed data (optional)

1–2 fictional rows for demo; **no real PHI**.
