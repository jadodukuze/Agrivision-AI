# AgriVision AI — Development Plan

## Phase 1: Foundation — completed
- [x] Create project documentation and repository structure.
- [x] Add responsive farmer-facing website.
- [x] Add FastAPI application and health endpoint.
- [x] Add GitHub Actions API test workflow.

## Phase 2: Secure platform foundation — implemented
- [x] Add SQLAlchemy database models for users, crop cases, and expert reviews.
- [x] Add configurable SQLite/MySQL database connection.
- [x] Add farmer registration and JWT login.
- [x] Hash passwords with Argon2.
- [x] Add role-protected farmer, expert, and administrator API routes.
- [x] Validate uploaded image contents and enforce size/type limits.
- [x] Persist crop cases and provide farmer case history.
- [x] Add expert review submission and basic user administration.
- [x] Connect the frontend to registration, login, case submission, and farmer history.

## Phase 3: User experience — next
- [ ] Build a complete expert dashboard with private image viewing and review history.
- [ ] Build a complete administrator dashboard for account and content management.
- [ ] Add case status updates, filters, pagination, and audit events.
- [ ] Add English and Kinyarwanda interface support.
- [ ] Improve accessibility and low-bandwidth mobile usability.

## Phase 4: AI and agricultural validation
- [ ] Select a suitable, licensed dataset with documented crop and disease classes.
- [ ] Check dataset quality, class balance, duplicate images, and label reliability.
- [ ] Split training, validation, and test data without data leakage.
- [ ] Train a baseline image classifier and record reproducible experiments.
- [ ] Evaluate per-class precision, recall, F1, confusion matrix, and calibration.
- [ ] Test on representative local field images before any pilot.
- [ ] Add an explicitly preliminary prediction workflow with confidence/uncertainty handling.
- [ ] Keep expert review and correction central; provide a safe fallback for unknown images.

## Phase 5: Production readiness
- [ ] Add Alembic database migrations.
- [ ] Move uploads to private persistent object storage and implement authorized image retrieval.
- [ ] Add rate limiting, request size limits, security headers, and stronger account controls.
- [ ] Add audit logging, monitoring, backups, and a retention/deletion policy.
- [ ] Add deployment configuration and secret management.
- [ ] Run security, accessibility, performance, and mobile tests.
- [ ] Prepare user guides and a supervised pilot plan.

## Responsible-use requirements
- Never present an unverified model output as a confirmed diagnosis.
- Do not prescribe pesticide products or application rates automatically.
- Make expert review available for uncertain or high-impact cases.
- Protect farmer accounts, photos, and personal information.
- Respect dataset licences and document model limitations.
