# AgriVision AI 🌱

**A crop-health case management and agricultural expert-review platform.**

AgriVision AI helps farmers submit crop photos, track crop-health cases, and receive expert-reviewed information. Automated disease diagnosis is **not currently enabled**.

## Implemented foundation

- Responsive website with farmer registration and sign-in.
- Farmer crop-photo submission and private case history.
- FastAPI backend with health endpoint and interactive API documentation.
- Password hashing and JWT authentication.
- Role-based farmer, expert, and administrator permissions.
- SQLAlchemy persistence with SQLite development support and MySQL through PyMySQL.\n- Versioned Alembic database migrations and CI migration smoke tests.
- Image content verification, 5 MB limit, and image-dimension checks.
- Authenticated expert queue, protected crop-photo access, and expert reviews.
- Administrator summary and privileged staff-account creation.
- One-time, secret-protected first-administrator bootstrap endpoint for deployed environments; local bootstrap script for development.
- GitHub Actions tests on Python 3.11 and 3.12.

## Roles

1. **Farmer:** register, submit crop photos, and view their own case history and expert reviews.
2. **Agricultural expert:** view submitted crop photos, assess cases, and record next steps.
3. **Administrator:** view platform counts and create expert or administrator accounts.

## Technology

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: SQLite for development; MySQL supported through SQLAlchemy/PyMySQL
- Authentication: Argon2 password hashing and JWT access tokens
- Image validation: Pillow
- CI: GitHub Actions and pytest

## Deploy to Render

A Render Blueprint is provided in `render.yaml` for a staging deployment. Follow [`docs/RENDER_DEPLOYMENT.md`](docs/RENDER_DEPLOYMENT.md) to connect GitHub and deploy. The free configuration is for testing only: its database expires after 30 days, the web service has no persistent disk, and uploaded photos are temporary. Do not use it for real farmer data. Durable database backups and private persistent image storage are required before production.

## First administrator on Render

Public registration creates farmer accounts only. To promote your already-registered account to the first administrator, follow the secure one-time procedure in [`docs/RENDER_DEPLOYMENT.md`](docs/RENDER_DEPLOYMENT.md#first-administrator). Remove the bootstrap token from Render immediately after successful setup.

## Local setup

Use Python 3.10 or newer. From the repository root:

```bash
cd backend
python -m venv .venv
```

Activate the environment, then install dependencies and prepare configuration:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Set a unique `JWT_SECRET_KEY`, and set the first administrator's name, email, and a unique password of at least 12 characters. Never commit `.env`.

### Create the first administrator

Run this once from the `backend` directory:

```bash
python create_admin.py
```

Public registration always creates farmer accounts. Only an existing administrator can create expert or additional administrator accounts.

### Start the backend

```bash
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`.

### Start the frontend

Open a second terminal at the repository root:

```bash
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`. The frontend uses the local API at `http://127.0.0.1:8000`. Set `CORS_ORIGINS` to the exact frontend origin if you use a different address.

## Database configuration

The example configuration uses SQLite for local development. To use MySQL, set `DATABASE_URL` in `backend/.env`, for example:

```text
mysql+pymysql://USER:PASSWORD@HOST:3306/agrivision_ai?charset=utf8mb4
```

The SQL reference schema is in `docs/database_schema.sql`. Alembic migrations are stored in `backend/migrations`. In development (`APP_ENV=development`), the API can create missing tables automatically. In production (`APP_ENV=production`), apply `python -m alembic upgrade head` before starting the API.

## Current limitations and next milestones

- Production deployment, HTTPS, backups, and monitoring are not configured.
- Local filesystem uploads must be replaced with private persistent object storage before multi-instance deployment.
- Rate limiting, account recovery, email verification, audit logging, and a full privacy/retention workflow remain to be implemented.
- English/Kinyarwanda translations and accessibility testing need further work.
- No trained or evaluated AI model is included. A suitable licensed dataset, reproducible training pipeline, held-out evaluation, and agricultural expert validation are required before enabling predictions.

## Responsible use and privacy

Do not commit secrets, passwords, private farmer information, or real uploaded crop photos. Restrict CORS and use private persistent storage in deployment. Any future AI output must be labelled preliminary and reviewed by a qualified agricultural expert. Do not automatically prescribe pesticide products or application rates.
