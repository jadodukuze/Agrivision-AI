# AgriVision AI API and database

## Implemented API
- `GET /` — service information and explicit AI availability flag.
- `GET /health` — health check.
- `POST /api/v1/auth/register` — create a farmer account. Public registration cannot assign privileged roles.
- `POST /api/v1/auth/login` — issue a short-lived JWT access token.
- `GET /api/v1/auth/me` — current authenticated user.
- `POST /api/v1/cases` — authenticated farmer submits a crop photo.
- `GET /api/v1/cases/mine` — farmer sees their own cases and expert reviews.
- `GET /api/v1/expert/cases` — expert/admin case queue.
- `POST /api/v1/expert/cases/{case_id}/review` — expert/admin records a review.
- `POST /api/v1/admin/users` — admin creates expert/admin accounts.
- `GET /api/v1/admin/summary` — admin dashboard counts.

## Data and configuration
SQLAlchemy supports SQLite for development and MySQL through PyMySQL. Set `DATABASE_URL` in a private `.env` file. The example MySQL URL is in `.env.example`. Tables are created at application startup for this starter release; production deployments should use versioned migrations.

Set a long random `JWT_SECRET_KEY`. Never use the CI test key in a deployed environment. Restrict `CORS_ORIGINS` to the real frontend origins. Keep uploads in private persistent storage and configure backups before production.

## Image safety
Uploads are limited to 5 MB, allow-listed by MIME type, verified against actual image format, and bounded by a pixel limit. Uploaded photos are not exposed through a public static URL.

## First administrator
Public registration always creates a farmer. Create the first administrator through a controlled database bootstrap process before using the admin-only staff creation endpoint. Do not add a public admin-registration route.

## Responsible AI
Automated disease classification is not implemented. Every new case remains pending expert review. Any future model must be evaluated on a properly licensed, representative dataset and its limitations documented. Model output must remain preliminary and must not automatically prescribe pesticide products or application rates.

## Local development
1. Copy `.env.example` to `.env` and set a unique secret.
2. Install `backend/requirements.txt`.
3. Run `uvicorn app.main:app --reload` from the `backend` folder.
4. Open `/docs` on the local API host.
5. Run tests with `python -m pytest -q` from `backend`.
