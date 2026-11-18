# AgriVision AI API and database

## Current implemented API

- `GET /` — project information.
- `GET /health` — checks API and database connectivity.
- `POST /api/v1/auth/register` — creates a farmer account.
- `POST /api/v1/auth/login` — returns a signed bearer token.
- `GET /api/v1/auth/me` — returns the authenticated account.
- `GET /api/v1/crops` — lists supported crop names.
- `POST /api/v1/cases` — authenticated farmer submits a crop photo and case details.
- `GET /api/v1/cases/mine` — farmer views their own submissions.
- `GET /api/v1/cases/{case_id}` — case detail and any expert review, subject to access rules.
- `GET /api/v1/cases/{case_id}/image` — private image access for the case owner or an authorised expert/admin.
- `GET /api/v1/expert/cases` — expert/admin case queue.
- `POST /api/v1/expert/cases/{case_id}/review` — expert/admin saves an assessment.
- `GET /api/v1/admin/users` — administrator lists accounts.
- `POST /api/v1/admin/users` — administrator creates expert or administrator accounts.
- `GET /api/v1/admin/summary` — administrator dashboard counts.
- `POST /api/v1/admin/users/{user_id}/deactivate` — administrator deactivates an account.

Interactive API documentation is available at `/docs`.

## Roles and security

Public registration always creates a farmer account. It cannot create an expert or administrator. Expert and administrator accounts must be provisioned by a trusted administrator/database operator. To bootstrap the first administrator, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` as private environment secrets before starting the API. Do not commit real secrets.

Passwords are hashed with Argon2. Access tokens are signed JWTs. Protected endpoints check the user's role and account status. Crop images are checked by decoding the actual image, not only by trusting the browser's content type.

## Database

The application uses SQLAlchemy models and creates the required tables on startup. SQLite is the default for development and tests. Set `DATABASE_URL` to a MySQL URL for deployment, for example:

```text
mysql+pymysql://USER:PASSWORD@HOST:3306/agrivision_ai?charset=utf8mb4
```

Create the database first and keep credentials in environment variables. Back up the database and uploaded image storage together. The SQL file in this folder is a reference schema; the SQLAlchemy models are the active application schema.

## Run locally

From the `backend` folder:

```bash
python -m venv .venv
# Activate the environment, then:
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Set a private `JWT_SECRET_KEY` and configure `DATABASE_URL` before production use.

## Important limitations

- The AI model is not implemented or trained yet. API responses explicitly report that no prediction is available.
- The current upload storage is local filesystem storage. Production needs private persistent object/file storage, backups, access-controlled image retrieval, and retention rules.
- Table creation is suitable for this starter project; a production release should introduce Alembic migrations.
- Configure HTTPS, trusted CORS origins, rate limiting, monitoring, and a managed secrets store before public deployment.
- Expert review text is informational. It should not automatically prescribe pesticide products or application rates.
