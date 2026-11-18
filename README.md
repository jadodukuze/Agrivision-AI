# AgriVision AI 🌱

**A crop-health support platform for farmers and agricultural experts.**

AgriVision AI helps farmers submit crop-leaf photos, record crop-health concerns, and prepare cases for agricultural expert review. The long-term goal is to add a properly evaluated AI image-classification model.

## Current implementation

- Responsive farmer-facing website.
- Crop case form with image preview and browser-side file checks.
- FastAPI service with health and project endpoints.
- Crop photo upload endpoint (JPG, PNG, WebP; maximum 5 MB).
- Server-side image-content verification (not only filename/MIME checks).
- Upload dimension limit to reduce decompression-bomb risk.
- CORS origins configurable through `AGRI_ALLOWED_ORIGINS`.
- Initial MySQL schema for users, crop cases, expert reviews, and AI predictions.
- Automated API tests and GitHub Actions.

## Important current limitations

This is still a **development prototype**, not a production-ready farmer service.

- User authentication and role-based permissions are not implemented.
- Case details are not yet persisted to MySQL; the current endpoint stores the validated image on the server filesystem only.
- Uploads require private persistent storage before public deployment.
- Farmer, expert, and administrator dashboards are not implemented.
- No trained or evaluated crop-disease model is included.
- Kinyarwanda interface support is planned, not yet implemented.

The API must not be treated as a disease diagnosis. A qualified agricultural expert should review crop concerns. Do not automatically prescribe pesticides or application rates.

## Technology

- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database target: MySQL (initial schema in `docs/database_schema.sql`)
- Planned AI: evaluated image-classification model trained with a suitable licensed dataset

## Run the backend locally

Use Python 3.10 or newer.

```bash
cd backend
python -m venv .venv
```

Activate the environment, then:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`.

## Run the frontend locally

Start a simple static server from the repository root:

```bash
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`. The form sends submissions to `http://127.0.0.1:8000/api/v1/cases`.

If the frontend uses a different origin, set `AGRI_ALLOWED_ORIGINS` before starting the backend. Separate origins with commas.

## Documentation

- `docs/PROJECT_PLAN.md` — implementation phases and progress.
- `docs/API_AND_DATABASE.md` — API details and known limitations.
- `docs/database_schema.sql` — initial MySQL schema.

## Privacy and security

Do not commit passwords, API keys, database credentials, private farmer data, or real uploaded crop photos. The current unauthenticated upload endpoint is intended only for local development and controlled demonstrations. Before deployment, implement authentication, authorization, rate limiting, private object storage, retention rules, audit logging, and production CORS settings.

## Development approach

Build in tested milestones: persistent database-backed cases and authentication; farmer/expert/admin workflows; reviewed AI integration; English/Kinyarwanda interface; then security hardening and deployment.
