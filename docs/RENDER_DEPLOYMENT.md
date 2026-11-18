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
Public registration creates farmer accounts only. An administrator must create expert accounts. The repository contains `backend/create_admin.py`, but the first administrator must be bootstrapped securely against the deployed database. Do not add administrator credentials to GitHub or expose a public admin-creation endpoint. Use an approved one-off command/shell workflow available on the selected Render plan before testing expert/admin workflows.

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
