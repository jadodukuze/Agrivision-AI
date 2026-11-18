# AgriVision AI 🌱

**A crop-health support platform for farmers and agricultural experts.**

AgriVision AI helps farmers create accounts, submit crop-health photos, track their cases, and receive human expert review. The project is designed to add a properly evaluated AI image-classification model in a later phase.

## Implemented in this version

- Responsive farmer-facing website.
- Farmer registration and sign-in.
- Password hashing with Argon2 and signed JWT authentication.
- Role-aware API access for farmers, experts, and administrators.
- Crop case submission with JPG, PNG, and WebP validation (maximum 5 MB).
- Persistent case metadata through SQLAlchemy.
- Farmer case history.
- Expert case queue and review submission endpoints.
- Basic administrator user listing and account deactivation endpoints.
- API documentation at `/docs`.
- Automated API tests with GitHub Actions.

## Not implemented yet

- **AI disease classification:** no trained or evaluated model is included yet. The application must not be used as an automated diagnosis tool.
- Full expert and administrator web dashboards.
- Kinyarwanda translations.
- Production image object storage and secure image viewing.
- Database migrations, deployment automation, monitoring, and backups.

## Technology

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: SQLAlchemy; SQLite for development/tests and MySQL for deployment
- Authentication: Argon2 password hashing and JWT
- Image validation: Pillow
- Planned AI: evaluated Python image-classification model using a suitable licensed dataset

## Run the backend

Use Python 3.10 or newer. From the `backend` directory:

```bash
python -m venv .venv
```

Activate the virtual environment, then:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set a private `JWT_SECRET_KEY`, then run:

```bash
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`.

SQLite is used by default. To use MySQL, create the `agrivision_ai` database and set `DATABASE_URL` in the environment:

```text
mysql+pymysql://USER:PASSWORD@HOST:3306/agrivision_ai?charset=utf8mb4
```

Never commit `.env`, passwords, JWT secrets, or real farmer data.

## Run the frontend

In a second terminal, from the `frontend` directory:

```bash
python -m http.server 5500
```

Open `http://127.0.0.1:5500`. The frontend expects the API at `http://127.0.0.1:8000`. Configure `CORS_ORIGINS` if the frontend uses another origin.

## Roles

1. **Farmer:** register, sign in, submit crop cases, and view personal case history.
2. **Expert:** review submitted cases and save assessments through the protected expert API.
3. **Administrator:** manage user accounts through the protected administration API.

Public registration always creates a farmer. It cannot create an expert or administrator. To bootstrap the first administrator, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` as private environment secrets before starting the API. Expert accounts must be provisioned by a trusted administrator/database operator. Never expose these credentials in GitHub source files.

## API documentation

See [docs/API_AND_DATABASE.md](docs/API_AND_DATABASE.md) for routes, roles, database configuration, and limitations.

## Responsible use, safety, and privacy

Crop symptoms can look similar, and image quality, lighting, and crop variety affect model performance. The current version does not run AI diagnosis. Expert guidance must be reviewed by qualified agricultural professionals. Do not automatically prescribe pesticide products or application rates. Protect farmer photos and personal information; use private persistent storage, access controls, HTTPS, backups, and a clear retention policy before production.

## Development plan

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md). The next phases are expert/admin web dashboards, secure image delivery, Kinyarwanda support, evaluated AI integration, and production deployment hardening.
