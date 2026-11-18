# AgriVision AI API and database

## Implemented API

- `GET /` — service information and explicit AI availability flag.
- `GET /health` — health check.
- `POST /api/v1/auth/register` — create a farmer account. Public registration cannot assign privileged roles.
- `POST /api/v1/auth/login` — issue a JWT access token.
- `GET /api/v1/auth/me` — current authenticated user.
- `POST /api/v1/cases` — authenticated farmer submits a crop photo.
- `GET /api/v1/cases/mine` — farmer sees their own cases and expert reviews.
- `GET /api/v1/expert/cases` — expert/admin case queue.
- `GET /api/v1/expert/cases/{case_id}/image` — authenticated expert/admin retrieves the submitted photo.
- `POST /api/v1/expert/cases/{case_id}/review` — expert/admin records an assessment and next steps.
- `POST /api/v1/admin/users` — administrator creates expert/admin accounts.
- `GET /api/v1/admin/summary` — administrator dashboard counts.

## Authentication and roles

Passwords are hashed with Argon2. Protected routes require an `Authorization: Bearer <token>` header. Public registration always creates a farmer. Role checks use the current database user record, not only the role claim inside the token.

The first administrator is provisioned using `python create_admin.py` from the backend folder. This script reads `ADMIN_FULL_NAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` from the private `.env` file and refuses to overwrite an existing account.

## Data and configuration

SQLAlchemy supports SQLite for development and MySQL through PyMySQL. Set `DATABASE_URL` in `backend/.env`. The example MySQL URL is in `.env.example`. Missing tables are created at startup for this starter release; production deployments should use versioned migrations.

Set a long random `JWT_SECRET_KEY`. Never use the CI test key in a deployed environment. Restrict `CORS_ORIGINS` to the real frontend origins. Keep uploads in private persistent storage and configure backups before production.

## Image safety

Uploads are limited to 5 MB, checked against their actual image format, and bounded by a pixel limit. Photos are not exposed through a public static URL. Only authenticated experts and administrators can retrieve uploaded case images through the protected image endpoint.

## Current limitations

- Automated crop-disease classification is not implemented.
- The app currently stores uploaded images on the local filesystem; production should use private persistent storage.
- Rate limiting, email verification, account recovery, audit logging, retention/deletion controls, HTTPS, backups, and monitoring remain to be implemented.
- The SQL reference schema mirrors the current SQLAlchemy user, case, and review models. AI prediction tables should be added with the future model integration.

## Responsible AI

Every new case remains pending expert review. Any future model must be evaluated on a properly licensed, representative dataset and its limitations documented. Model output must remain preliminary and must not automatically prescribe pesticide products or application rates.

## Local development

1. Copy `.env.example` to `.env` and set unique secrets.
2. Install `backend/requirements.txt`.
3. Run `python -m alembic upgrade head` to create the database tables.\n4. Run `python create_admin.py` once to provision the first administrator.
5. Start `uvicorn app.main:app --reload` from the `backend` folder.
6. Start the frontend with `python -m http.server 5500 --directory frontend` from the repository root.
7. Run tests with `python -m pytest -q` from `backend`.
