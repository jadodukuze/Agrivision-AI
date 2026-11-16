# AgriVision AI 🌱

**AI-assisted crop disease identification for farmers.**

AgriVision AI is a web application concept that helps farmers submit crop-leaf photos, receive a preliminary AI-assisted disease assessment, and access practical prevention guidance. It is a decision-support tool, not a replacement for an agricultural expert.

## Project goals

- Make it easier to report and review crop health problems.
- Provide clear guidance in English and Kinyarwanda.
- Help agricultural experts review farmer-submitted cases.
- Keep records of submitted crop images and assessment results.

## Planned technology

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **Database:** MySQL
- **AI:** Python image-classification model (to be integrated and evaluated)

## Main user roles

1. **Farmer:** submits crop photos and views assessment history.
2. **Agricultural expert:** reviews cases and provides verified advice.
3. **Administrator:** manages users, crop information, and platform content.

## Current development status

This repository starts with the project foundation. AI predictions are not yet implemented. Until a model is trained, tested, and connected, the application must not claim to diagnose crop diseases.

## Planned development stages

1. Project structure and documentation.
2. Responsive frontend.
3. FastAPI backend and API health check.
4. MySQL database design and integration.
5. Image upload with validation and secure storage.
6. AI model integration and evaluation.
7. Farmer and expert dashboards.
8. Testing, deployment, and user documentation.

## Run the backend

Use Python 3.10 or newer.

```bash
cd backend
python -m venv .venv
```

Activate the environment, then install dependencies:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API documentation at `http://127.0.0.1:8000/docs`.

## Important safety and accuracy note

An image-based prediction can be wrong because of lighting, image quality, crop variety, or similar-looking symptoms. Users should treat results as preliminary and consult a qualified agricultural expert before taking important crop-treatment decisions. The project will not recommend pesticide use without verified, crop-specific guidance.

## Contribution

Work in small, tested steps. Never commit passwords, API keys, database credentials, private farmer data, or real uploaded crop images.