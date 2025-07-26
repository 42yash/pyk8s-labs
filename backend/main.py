# backend/main.py
from fastapi import FastAPI
from core.config import settings
from api import router as api_router # Import the router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1") # Include the router

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}