# backend/websocket_manager.py
import asyncio
import json
from datetime import datetime
from typing import Dict, Set

import docker
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

import crud
from core.config import settings
from jose import JWTError, jwt

REDIS_CHANNEL = "cluster-status"


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            print(f"CRITICAL: Failed to initialize Docker client: {e}")
            self.docker_client = None

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        print(f"WebSocket connected for user: {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        print(f"WebSocket disconnected for user: {user_id}")

    async def send_json(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except (WebSocketDisconnect, RuntimeError):
            pass

    async def broadcast_to_user(self, user_id: str, data: dict):
        if user_id in self.active_connections:
            # Create a copy of the set to avoid issues if a connection is removed during iteration
            for connection in list(self.active_connections[user_id]):
                await self.send_json(connection, data)

    async def handle_terminal_session(
        self, websocket: WebSocket, user_id: str, cluster_id: str, db: Session
    ):
        if not self.docker_client:
            await self.send_json(
                websocket,
                {
                    "type": "terminal_error",
                    "payload": "Docker client not available on server.",
                },
            )
            return

        user_obj = (
            db.query(crud.models.User).filter(crud.models.User.id == user_id).first()
        )
        cluster = crud.get_cluster(db, cluster_id=cluster_id)
        if not cluster or cluster.user_id != user_obj.id:
            await self.send_json(
                websocket,
                {
                    "type": "terminal_error",
                    "payload": "Access denied or cluster not found.",
                },
            )
            return

        if cluster.status != "RUNNING":
            await self.send_json(
                websocket,
                {
                    "type": "terminal_error",
                    "payload": f"Cluster is not in 'RUNNING' state.",
                },
            )
            return

        container_name = f"kind-{cluster.name}-control-plane"
        try:
            container = self.docker_client.containers.get(container_name)
            exit_code, sock = container.exec_run(
                cmd="bash", stdin=True, tty=True, socket=True
            )

            # The socket from exec_run is a raw socket. We need to handle it carefully.
            exec_socket = sock._sock

            loop = asyncio.get_event_loop()

            async def ws_to_docker():
                try:
                    while True:
                        msg = await websocket.receive_json()
                        if msg.get("type") == "terminal_data":
                            await loop.sock_sendall(
                                exec_socket, msg["payload"].encode("utf-8")
                            )
                except WebSocketDisconnect:
                    pass

            async def docker_to_ws():
                try:
                    while True:
                        data = await loop.sock_recv(exec_socket, 1024)
                        if not data:
                            break
                        await self.send_json(
                            websocket,
                            {
                                "type": "terminal_data",
                                "payload": data.decode("utf-8", errors="ignore"),
                            },
                        )
                except Exception:
                    pass

            ws_task = asyncio.create_task(ws_to_docker())
            docker_task = asyncio.create_task(docker_to_ws())
            done, pending = await asyncio.wait(
                [ws_task, docker_task], return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()

        except docker.errors.NotFound:
            await self.send_json(
                websocket,
                {
                    "type": "terminal_error",
                    "payload": f"Container '{container_name}' not found.",
                },
            )
        except Exception as e:
            await self.send_json(
                websocket,
                {"type": "terminal_error", "payload": f"Terminal failed: {str(e)}"},
            )
        finally:
            print(f"Terminal session ended for cluster {cluster_id}")


manager = ConnectionManager()


async def get_current_user_from_token(token: str, db: Session):
    if not token:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if not email:
            return None
        user = crud.get_user_by_email(db, email=email)
        return user
    except JWTError:
        return None
