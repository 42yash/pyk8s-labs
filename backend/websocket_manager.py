# backend/websocket_manager.py
import asyncio
import json
from typing import Dict

from fastapi import Depends, WebSocket, WebSocketDisconnect, Query, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

import crud
import models
from core.config import settings
from db import get_db
from redis_client import get_redis_connection

# Channel for publishing cluster status updates
REDIS_CHANNEL = "cluster-status"

class ConnectionManager:
    def __init__(self):
        # Maps user_id to their active WebSocket connection
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_text(message)

manager = ConnectionManager()

async def get_current_user_from_token(
    token: str = Query(...), db: Session = Depends(get_db)
) -> models.User | None:
    """
    WebSocket dependency to get the current user from a JWT in a query param.
    Returns None if token is invalid, allowing the connection to be closed gracefully.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = crud.get_user_by_email(db, email=email)
    return user


async def redis_listener(manager: ConnectionManager):
    """
    Listens to a Redis Pub/Sub channel for status updates and pushes
    them to the relevant user's WebSocket connection.
    """
    redis_conn = get_redis_connection()
    pubsub = redis_conn.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    
    print("Redis Pub/Sub listener started...")
    try:
        while True:
            # The 'ignore_subscribe_messages' is important to skip confirmation messages
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                print(f"Received message from Redis: {message['data']}")
                try:
                    # The message data is expected to be a JSON string
                    data = json.loads(message["data"])
                    user_id = data.get("user_id")
                    if user_id:
                        # Forward the original data as a JSON string to the client
                        await manager.send_personal_message(message["data"], user_id)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error processing Redis message: {e}")
            await asyncio.sleep(0.01) # prevent high CPU usage
    except asyncio.CancelledError:
        print("Redis listener task cancelled.")
    finally:
        await pubsub.unsubscribe(REDIS_CHANNEL)
        await pubsub.close()
        print("Redis Pub/Sub listener stopped.")