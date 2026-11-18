# AgriVision AI — Development Plan

## Phase 1: Foundation
- [x] Create project documentation.
- [x] Add initial frontend landing page.
- [x] Add FastAPI application and health endpoint.
- [x] Add repeatable API tests and GitHub Actions CI.
- [ ] Verify the complete application locally and in a deployed environment.

## Phase 2: Data and API
- [x] Design MySQL tables for users, crop cases, and expert reviews.
- [x] Add environment-based configuration and SQLAlchemy persistence (SQLite development; MySQL supported).
- [x] Add farmer registration, password hashing, JWT authentication, and role checks.
- [x] Add authenticated crop submissions and farmer case history.
- [x] Add expert case queue and review workflow.
- [x] Add admin summary and privileged staff-account creation endpoint.
- [x] Validate uploaded image content, size, format, and dimensions.
- [ ] Add versioned database migrations and a controlled first-admin bootstrap.
- [ ] Add private persistent object storage and authenticated image retrieval.

## Phase 3: AI and expert review
- [ ] Select a suitable, licensed and representative crop image dataset.
- [ ] Train and evaluate crop-specific image classification models.
- [ ] Establish independent validation, class-level metrics, and model cards.
- [ ] Add an opt-in preliminary prediction workflow with uncertainty handling.
- [ ] Keep expert review and correction as mandatory safeguards for consequential guidance.

## Phase 4: User experience
- [x] Initial responsive public landing page and photo submission form.
- [ ] Farmer dashboard connected to registration, login, and case-history APIs.
- [ ] Expert dashboard connected to case queue and review APIs.
- [ ] Administrator dashboard connected to management APIs.
- [ ] English and Kinyarwanda interface support.
- [ ] Accessibility and low-bandwidth improvements.

## Phase 5: Quality and release
- [x] Automated API tests and GitHub Actions CI.
- [ ] Expand tests for permissions, database failures, uploads, and review lifecycle.
- [ ] Security and privacy review, rate limiting, audit logging, and backup/restore tests.
- [ ] Production deployment, monitoring, and operational documentation.
- [ ] Pilot testing with farmers and qualified agricultural experts.

## Responsible-use requirements
- Never present an unverified model output as a confirmed diagnosis.
- Do not prescribe pesticide products or application rates automatically.
- Make qualified expert review available for uncertain or high-impact cases.
- Protect farmer accounts, photos, and personal information.
- Do not train on farmer-submitted photos without an appropriate consent and data-governance process.
