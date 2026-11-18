# AgriVision AI — Development Plan

## Phase 1: Working platform foundation
- [x] Create project documentation and initial MySQL schema.
- [x] Add responsive website and crop photo submission.
- [x] Add FastAPI health endpoint and API documentation.
- [x] Add farmer registration, login, password hashing, and JWT authentication.
- [x] Add database models and SQLite/MySQL connection configuration.
- [x] Add farmer case submission and personal case history.
- [x] Add expert queue, protected photo retrieval, and review workflow.
- [x] Add administrator summary and staff account creation.
- [x] Add a secure first-administrator bootstrap script.
- [x] Add automated API tests and CI for Python 3.11 and 3.12.

## Phase 2: Production readiness
- [x] Add versioned Alembic database migrations and CI migration checks.
- [ ] Replace local uploads with private persistent object storage.
- [ ] Add rate limiting, email verification, account recovery, and audit logs.
- [ ] Add privacy retention/deletion controls, backups, and monitoring.
- [ ] Deploy with HTTPS and production CORS configuration.
- [ ] Complete accessibility and mobile testing.

## Phase 3: Farmer and expert experience
- [x] Farmer account, submission, and case history screens.
- [x] Expert case queue and review screen.
- [x] Administrator summary and staff account management screen.
- [ ] Add case assignment, review status workflow, and review notifications.
- [ ] Complete English and Kinyarwanda translations.

## Phase 4: AI and agricultural validation
- [ ] Select a suitable, licensed, representative crop image dataset.
- [ ] Build reproducible training and evaluation pipelines.
- [ ] Evaluate per-class precision, recall, F1, confusion matrix, and calibration on held-out data.
- [ ] Add model versioning, confidence thresholds, and expert correction workflow.
- [ ] Enable preliminary predictions only after agricultural expert validation.

## Responsible-use requirements
- Never present an unverified model output as a confirmed diagnosis.
- Do not automatically prescribe pesticide products or application rates.
- Keep expert review available for uncertain or high-impact cases.
- Protect farmer accounts, photos, and personal information.
- Do not claim model accuracy until measured on a held-out test set.
