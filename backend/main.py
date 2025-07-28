# backend/main.py
import asyncio
import json
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
from api import router as api_router, run_cluster_deletion
from core.config import settings
from db import SessionLocal, get_db
from redis_client import get_redis_connection
from websocket_manager import (
    REDIS_CHANNEL,
    ConnectionManager,
    get_current_user_from_token,
    manager,
)

origins = ["http://localhost:3000", "http://0.0.0.0:3000", "http://127.0.0.1:3000"]


async def check_expired_clusters():
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


async def redis_listener(manager: ConnectionManager):
    redis_conn = get_redis_connection()
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    print("Subscribed to Redis channel and listening for messages...")
    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    user_id = data.get("user_id")
                    if user_id:
                        await manager.broadcast_to_user(
                            str(user_id),
                            {"type": "cluster_status_update", "payload": data},
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Could not process Redis message: {e}")
    except Exception as e:
        print(f"Redis listener error: {e}")
    finally:
        await pubsub.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_expired_clusters, "interval", minutes=5)
    scheduler.start()
    redis_task = asyncio.create_task(redis_listener(manager))
    yield
    scheduler.shutdown()
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    user = await get_current_user_from_token(token, db)
    if not user:
        await websocket.close(code=1008, reason="Invalid credentials.")
        return

    user_id = str(user.id)
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "start_terminal":
                cluster_id = data.get("cluster_id")
                if cluster_id:
                    await manager.handle_terminal_session(
                        websocket, user_id, cluster_id, db
                    )
                    # Once the terminal session ends, break the loop to disconnect
                    break

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        print(f"Error in WebSocket endpoint: {e}")
        manager.disconnect(websocket, user_id)


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
