# Deployment

## Goals

- **Public HTTPS URL** for the FastAPI app (Vapi webhooks must reach it).
- **Dialable U.S. number** on the assistant.
- **Database** reachable from the app (Postgres on Railway or SQLite with persistent volume — note SQLite limits on PaaS restarts).

## Railway (backend + optional Postgres)

1. Create a Railway project; add **GitHub** repo or deploy from CLI (`railway up` when ready).
2. Add **PostgreSQL** plugin if not using SQLite; copy `DATABASE_URL` into service variables.
3. Set environment variables: `GROQ_API_KEY`, `VAPI_*`, `DATABASE_URL`, `PUBLIC_URL` (your Railway **public domain**).
4. Ensure the service **exposes** the port your ASGI server uses (e.g. `8000`); set start command (e.g. `uvicorn app.main:app --host 0.0.0.0 --port $PORT` if Railway injects `PORT`).
5. Deploy; open **Deployments → Networking** and confirm the **public URL**.
6. Health check: `GET /` or `/health` if implemented.

## Vapi

1. Create an assistant aligned with your webhook contract.
2. Set **server URL** to `https://<your-public-host>/<webhook-path>` (exact path your FastAPI app defines).
3. Provision and attach a **U.S. phone number**; test inbound call.
4. Store `VAPI_API_KEY` (and any webhook secret) in Railway, not in git.

## Local development with tunnel

If you cannot expose localhost directly:

1. Run the API locally.
2. Run **ngrok** (or similar): `ngrok http 8000`.
3. Put the **https** forwarding URL into Vapi as the webhook base; update `PUBLIC_URL` for any absolute links.

Document the tunnel URL in README if reviewers must use it temporarily.

## If phone provisioning fails (FAQ)

Per assessment: **document** what you tried (provider, errors, timelines). Provide **working** local or tunneled setup with steps. You are evaluated on how you handled the blocker, not penalized for vendor issues alone.

## Verification checklist

- [ ] Call the number; complete a full registration with confirmation.
- [ ] `GET /patients` shows the new row.
- [ ] Redeploy or restart service; data still present.
- [ ] Logs show **final payload** (or summary) on stdout.

## Submission bundle

Include in README (or cover email): **repo URL**, **phone number**, **API base URL**, and any **test notes** (demo credentials, seed data, limitations).
