# AgriVision AI API and database notes

## Current API
- `GET /`: basic project information.
- `GET /health`: service health check.
- `POST /api/v1/cases`: accepts farmer_name, crop_name, optional location and description, and an image file (JPG/PNG/WebP, maximum 5 MB). Stores the file and returns a pending expert-review case ID.

**Important:** The current upload endpoint stores images on the server filesystem only. It does not yet persist case metadata to MySQL, authenticate users, or run an AI model. The upload directory must use persistent private storage in deployment. Restrict CORS to the real frontend origin before production.

## MySQL
Run `database_schema.sql` in MySQL to create the initial users, crop_cases, expert_reviews, and ai_predictions tables. Database connection code and authenticated case persistence are the next implementation step.

## Run API locally
1. Install dependencies from `backend/requirements.txt`.
2. Start from the `backend` directory with `uvicorn app.main:app --reload`.
3. Visit `http://127.0.0.1:8000/docs`.
