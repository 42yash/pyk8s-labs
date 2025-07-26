# backend/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from api import router as api_router, run_cluster_deletion
import crud
from db import SessionLocal

def check_expired_clusters():
    """Scheduled job to find and delete expired clusters."""
    print("Running TTL cleanup job...")
    db = SessionLocal()
    try:
        expired_clusters = crud.get_expired_clusters(db)
        if not expired_clusters:
            print("No expired clusters found.")
            return

        for cluster in expired_clusters:
            print(f"Found expired cluster: {cluster.name} (ID: {cluster.id})")
            # Update status to DELETING to prevent race conditions
            cluster.status = "DELETING"
            db.commit()
            # Run deletion in the background
            run_cluster_deletion(cluster.name, cluster.id, db)
    finally:
        db.close()

# Use the new lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_expired_clusters, 'interval', minutes=5)
    scheduler.start()
    print("Scheduler started...")
    yield
    # On shutdown
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}