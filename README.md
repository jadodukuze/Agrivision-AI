# AgriVision AI 🌱

**A crop-health support platform for farmers and agricultural experts.**

AgriVision AI is being developed to help farmers submit crop-leaf photos, keep a record of crop-health concerns, and receive expert-reviewed information. The long-term goal is to add an evaluated AI image-classification model.

## Current starter features
- Responsive farmer-facing website.
- Crop case form with image preview and browser-side file checks.
- FastAPI service with health endpoint.
- Crop photo upload endpoint (JPG, PNG, WebP; maximum 5 MB).
- Initial MySQL schema for users, crop cases, expert reviews, and AI predictions.
- Initial API tests and GitHub Actions workflow.

**Not implemented yet:** user authentication, persistent MySQL case storage, farmer/expert/admin dashboards, Kinyarwanda translation, and AI model inference. The current upload API stores images on the server filesystem and returns a pending expert-review status. It must not be treated as a disease diagnosis.

## Technology
- Frontend: HTML, CSS, JavaScript
- Backend: Python, FastAPI
- Database: MySQL (initial schema in `docs/database_schema.sql`)
- Planned AI: Python image-classification model, to be trained and evaluated using a suitable licensed dataset

## User roles planned
1. Farmer — submit crop photos and view case history.
2. Agricultural expert — review cases and provide verified guidance.
3. Administrator — manage accounts, crop information, and platform content.

## Run the backend locally
Use Python 3.10 or newer.

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment, then:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`.
Open `frontend/index.html` in a browser for the interface. The form expects the local API at `http://127.0.0.1:8000`.

## Documentation
- `docs/PROJECT_PLAN.md` — development phases.
- `docs/API_AND_DATABASE.md` — API details and current limitations.
- `docs/database_schema.sql` — initial MySQL schema.

## Responsible use and privacy
An image-based model can be wrong because of lighting, image quality, crop variety, and similar-looking symptoms. Any future prediction must be labelled preliminary and reviewed by a qualified agricultural expert. Do not automatically prescribe pesticides or treatment rates. Do not commit passwords, API keys, database credentials, private farmer data, or real uploaded crop photos. Configure private persistent image storage and restrict CORS before deployment.

## Development approach
Build and test the platform in small phases: authentication and database persistence; farmer, expert, and admin dashboards; reviewed AI integration; English/Kinyarwanda interface; then security, accessibility, and deployment.
