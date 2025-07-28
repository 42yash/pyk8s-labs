# backend/main.py
import asyncio
import json
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.orm import Session

import crud
from api import router as api_router, run_cluster_deletion
from core.config import settings
from core.security import get_current_user_from_query
from db import SessionLocal
from models.user import User
from redis_client import get_redis_connection
from websocket_manager import REDIS_CHANNEL

origins = ["http://localhost:3000", "http://0.0.0.0:3000", "http://127.0.0.1:3000"]


async def check_expired_clusters():
    """Scheduled job to find and delete expired clusters."""
    db = SessionLocal()
    try:
        expired_clusters = crud.get_expired_clusters(db)
        for cluster in expired_clusters:
            if cluster.status not in ["DELETING", "PROVISIONING"]:
                print(
                    f"Scheduling expired cluster for deletion: {cluster.name} ({cluster.id})"
                )
                cluster.status = "DELETING"
                db.commit()
                # Schedule the deletion as a background task in the event loop
                asyncio.create_task(
                    run_cluster_deletion(
                        str(cluster.id),
                        cluster.name,
                        str(cluster.user_id),
                        cluster.provider,
                    )
                )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the FastAPI app."""
    # Start the background scheduler for TTL checks
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_expired_clusters, "interval", minutes=5)
    scheduler.start()

    # The Redis listener logic is now handled per-client in the /events endpoint
    yield

    # Shutdown the scheduler on application exit
    scheduler.shutdown()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the standard REST API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/api/v1/events")
async def sse_events(
    request: Request,
    current_user: User = Depends(get_current_user_from_query),
):
    """
    Server-Sent Events endpoint.
    A client subscribes to this endpoint to receive real-time status updates
    for their resources.
    """
    user_id = str(current_user.id)
    redis_conn = get_redis_connection()
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)

    async def event_generator():
        try:
            while True:
                # Check if the client has disconnected
                if await request.is_disconnected():
                    print(f"Client disconnected from SSE for user {user_id}")
                    break

                # Listen for messages from Redis
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        # Only send the event if it belongs to the authenticated user
                        if data.get("user_id") == user_id:
                            # SSE format: "data: <json_string>\n\n"
                            yield f"data: {message['data']}\n\n"
                    except (json.JSONDecodeError, KeyError) as e:
                        print(f"Could not process Redis message for SSE: {e}")

                # Yield a keep-alive comment to prevent connection timeouts
                yield ": keep-alive\n\n"
                await asyncio.sleep(15)

        except asyncio.CancelledError:
            print(f"SSE connection cancelled for user {user_id}.")
        finally:
            # Clean up the Redis subscription when the connection is closed
            await pubsub.close()
            print(f"Closed Redis pubsub for user {user_id}.")

    return EventSourceResponse(event_generator())


@app.get("/")
def read_root():
    """Root endpoint for basic health check."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
