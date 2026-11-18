# AgriVision AI API and database notes

## Current API

- `GET /`: project status and documentation path.
- `GET /health`: service health check.
- `POST /api/v1/cases`: accepts `farmer_name`, `crop_name`, optional `location` and `description`, and an image file (JPG/PNG/WebP, maximum 5 MB).

The upload endpoint checks the actual image bytes and format, rejects invalid files, limits image dimensions, and saves accepted images under `backend/storage/uploads` using a generated UUID filename.

Example form fields:

- `farmer_name` (required, 2–100 characters)
- `crop_name` (required, 2–80 characters)
- `location` (optional, up to 120 characters)
- `description` (optional, up to 1,000 characters)
- `image` (required; JPG, PNG, or WebP; up to 5 MB)

## Current limitations

The current upload endpoint stores the image on the server filesystem only. It does not yet persist case metadata to MySQL, authenticate users, or run an AI model. It is suitable only for local development and controlled demonstrations. Do not expose it as a public production service.

Before production, implement authenticated ownership checks, database transactions, private persistent image storage, upload rate limiting, retention/deletion controls, audit logs, and strict CORS origins.

## MySQL

Run `database_schema.sql` in MySQL to create the initial users, crop_cases, expert_reviews, and ai_predictions tables. Database connection code and authenticated case persistence are still pending.

## Run API locally

1. Install dependencies from `backend/requirements.txt`.
2. Start from the `backend` directory with `uvicorn app.main:app --reload`.
3. Visit `http://127.0.0.1:8000/docs`.

## CORS

The local frontend server runs at `http://127.0.0.1:5500`. To use another origin, set `AGRI_ALLOWED_ORIGINS` to a comma-separated list of exact origins before starting the API.
