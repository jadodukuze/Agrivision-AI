# Deploy AgriVision AI to Render (staging)

This repository includes a Render Blueprint at the repository root. The initial Blueprint is a staging/demo deployment, not production.

## What it creates
- One Python web service running FastAPI and serving the HTML/CSS/JavaScript frontend from the same HTTPS origin.
- One Render PostgreSQL database.
- Alembic migrations run before the API starts.
- A generated JWT secret stored as a Render environment variable.
- A `/health` health-check endpoint.

## Connect the GitHub repository
1. Sign in to Render and open the Dashboard.
2. Choose **New + → Blueprint**.
3. Connect GitHub if requested, then select `jadodukuze/Agrivision-AI`.
4. Select branch `deploy/render-staging` while reviewing this pull request, or select `main` after merging the deployment changes.
5. Render reads `render.yaml`. Review the services, plan and charges shown before applying.
6. Apply the Blueprint and wait for deployment to finish.
7. Open the service URL. The website should load. Add `/health` to check the API and `/docs` to inspect API documentation.

## Important free-plan limitations
This Blueprint uses free resources for staging. Render free web services have no persistent disk. Free Render Postgres databases expire after 30 days and have no backups. Do not use this configuration for real farmer data, personal information, or important crop photographs.

The current upload implementation writes images to the local filesystem. In this Blueprint the upload directory is temporary. A restart or redeploy can remove uploaded images. Before production, implement private object storage (or an appropriately secured paid persistent disk), configure backups, and use a database plan with durable retention.

## First administrator
Public registration creates farmer accounts only. The API provides a one-time, secret-protected bootstrap endpoint for the first administrator.

1. Register your intended administrator account through the website first.
2. In the Render Dashboard, open the `agrivision-ai-api` service and go to **Environment**.
3. Add `ADMIN_BOOTSTRAP_EMAIL` with the exact email address of that registered account.
4. Add `ADMIN_BOOTSTRAP_TOKEN` with a randomly generated secret of at least 32 characters. Generate one locally with Python: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Do not put this value in GitHub, source code, chat, or screenshots.
5. Save the environment changes and wait for Render to redeploy.
6. Open `/docs`, find `POST /api/v1/admin/bootstrap`, click **Try it out**, and submit the registered email plus the secret in `setup_token`.
7. Confirm the response reports role `admin`.
8. Immediately return to Render **Environment**, delete `ADMIN_BOOTSTRAP_TOKEN`, save, and wait for redeployment. The endpoint then disables itself. Keep `ADMIN_BOOTSTRAP_EMAIL` or remove it too; it is not a credential.

The endpoint only promotes the one configured, already-registered account; it refuses incorrect secrets, a different email, missing accounts, and any attempt after an administrator exists. It does not accept passwords or create public administrator accounts. Sign out of the website and sign in again so the browser receives a fresh token containing the administrator role.

Never share the bootstrap token, passwords, or access tokens. If the token is exposed before use, replace it in Render before continuing.

## Production checklist
- Choose a database with durable storage, backups, and a retention policy.
- Replace temporary local image storage with private object storage and verify authenticated image access.
- Bootstrap the first administrator securely and rotate any bootstrap secret immediately.
- Implement rate limiting, account recovery, email verification, audit logging, and privacy/retention controls.
- Test registration, login, farmer submission/history, expert review, admin actions, image persistence, and backup restoration.
- AI diagnosis is not included or enabled in this version; do not present expert-review status as an AI prediction.

## Render service settings
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`

Never commit secrets or production database URLs.
