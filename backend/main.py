# backend/main.py
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings
from api import router as api_router, run_cluster_deletion # Import the async task
import crud
from db import SessionLocal
from websocket_manager import manager, redis_listener
import logging

origins = [
    "http://localhost:3000",
    "http://0.0.0.0:3000",
    "http://127.0.0.1:3000",
]

async def check_expired_clusters():
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
            cluster.status = "DELETING"
            db.commit()
            
            # Call the async task directly, without passing the db session
            asyncio.create_task(
                run_cluster_deletion(cluster.name, str(cluster.id), str(cluster.user_id))
            )
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_expired_clusters, 'interval', minutes=5)
    scheduler.start()
    print("Scheduler started...")

    redis_task = asyncio.create_task(redis_listener(manager))
    
    yield
    
    # On shutdown
    print("Shutting down...")
    redis_task.cancel()
    scheduler.shutdown()
    try:
        await redis_task
    except asyncio.CancelledError:
        print("Redis listener task was cancelled successfully.")
    print("Scheduler and Redis listener shut down.")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.middleware("http")
async def log_requests(request, call_next):
    logging.info(f"Request: {request.method} {request.url} from origin {request.headers.get('origin')}")
    response = await call_next(request)
    logging.info(f"Response status: {response.status_code}")
    return response

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}