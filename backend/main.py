from fastapi import FastAPI
from core.config import settings # Import the settings object

app = FastAPI(title=settings.PROJECT_NAME) # Use project name in title

@app.get("/api/v1")
def read_root():
    # Use a setting in the response body
    return {"message": f"Hello from {settings.PROJECT_NAME} Backend"}