from fastapi import FastAPI

app = FastAPI(
    title="AgriVision AI",
    description=(
        "A decision-support platform for preliminary crop disease "
        "assessment and agricultural expert review."
    ),
    version="0.1.0",
)


@app.get("/", tags=["General"])
def read_root():
    return {
        "project": "AgriVision AI",
        "message": "Welcome to AgriVision AI API",
        "status": "development",
    }


@app.get("/health", tags=["General"])
def health_check():
    return {"status": "ok"}
