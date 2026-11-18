# AgriVision AI 🌱

**A crop-health case management and agricultural expert-review platform.**

AgriVision AI helps farmers submit crop photos, track crop-health cases, and receive expert-reviewed information. It is designed for a responsible future AI-assisted workflow; automated disease diagnosis is **not currently enabled**.

## Implemented foundation
- Responsive farmer-facing website and crop-photo submission form.
- FastAPI backend with health endpoint and interactive API documentation.
- Farmer registration, password hashing, JWT login, and profile endpoint.
- Role-based access for farmers, experts, and administrators.
- Persistent SQLAlchemy data models with SQLite development support and MySQL support.
- Authenticated crop-case submission and farmer case history.
- Image type/content verification, 5 MB limit, and image dimension checks.
- Expert case queue and review submission.
- Admin summary and privileged staff-account creation endpoint.
- GitHub Actions CI with API tests.

## Roles
1. **Farmer:** register, submit crop photos, and view their own case history and reviews.
2. **Agricultural expert:** review submitted cases and record assessments.
3. **Administrator:** view platform summary and create expert/admin accounts.

## Technology
- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: SQLite for development; MySQL supported through SQLAlchemy/PyMySQL
- Authentication: Argon2 password hashing and JWT access tokens
- Image validation: Pillow
- CI: GitHub Actions and pytest

## Run the backend
Use Python 3.10 or newer.

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, install dependencies, copy `.env.example` to `.env`, and set a unique `JWT_SECRET_KEY`.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`.

## Current limitations and next milestones
- The existing public website still needs full login, farmer, expert, and admin dashboard screens connected to the API.
- The first administrator must be provisioned through a controlled database bootstrap procedure.
- Production database migrations, private object storage, deployment configuration, backups, monitoring, and security review remain required.
- Automated AI classification is not implemented. A licensed dataset, reproducible training pipeline, independent evaluation, and expert validation are required before enabling it.
- English/Kinyarwanda translation and accessibility improvements remain planned.

See `docs/PROJECT_PLAN.md` and `docs/API_AND_DATABASE.md`.

## Safety, privacy, and responsible use
Do not commit secrets, passwords, private farmer information, or real uploaded crop photos. Restrict CORS and use private persistent storage in deployment. AI outputs, when eventually implemented, must be labelled preliminary and reviewed by a qualified agricultural expert. Do not automatically prescribe pesticide products or application rates.
