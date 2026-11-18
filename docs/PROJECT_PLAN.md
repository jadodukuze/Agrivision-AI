# AgriVision AI — Development Plan

## Phase 1: Foundation
- [x] Create project documentation.
- [x] Add initial frontend landing page.
- [x] Add FastAPI application and health endpoint.
- [x] Add responsive crop-case form and browser-side image preview.
- [x] Connect the form to the API.
- [x] Validate uploaded image contents, file size, and dimensions on the server.
- [ ] Verify the starter application locally on a Windows computer.

## Phase 2: Data and API
- [x] Design initial MySQL tables for users, crop cases, and expert reviews.
- [ ] Add database configuration through environment variables.
- [ ] Persist crop-case metadata in MySQL.
- [ ] Add secure user authentication and role-based access.
- [ ] Add private, persistent image storage and retention controls.
- [ ] Add rate limiting and production CORS configuration.

## Phase 3: User workflows
- [ ] Farmer registration, login, dashboard, and submission history.
- [ ] Expert dashboard, case assignment, and review workflow.
- [ ] Administrator dashboard and account management.
- [ ] English and Kinyarwanda interface support.

## Phase 4: AI and expert review
- [ ] Select a suitable, licensed crop image dataset with clear provenance.
- [ ] Train and evaluate a crop image classification model.
- [ ] Report per-class precision, recall, F1, confusion matrix, and limitations.
- [ ] Add model versioning and expert correction workflow.
- [ ] Clearly label model outputs as preliminary and uncertain where appropriate.

## Phase 5: Quality and release
- [x] Add initial automated API tests and GitHub Actions.
- [ ] Expand unit, integration, and security tests.
- [ ] Review privacy, accessibility, and security.
- [ ] Test on mobile screens and slower connections.
- [ ] Prepare deployment and user documentation.

## Responsible-use requirements
- Never present an unverified model output as a confirmed diagnosis.
- Do not prescribe pesticide products or application rates automatically.
- Make expert review available for uncertain or high-impact cases.
- Protect farmer accounts, photos, and personal information.
- Do not claim model accuracy until it has been measured on a held-out test set.
