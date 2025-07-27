import asyncio
import os
import pty
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

import crud
import models
from db import get_db
from websocket_manager import get_current_user_from_token

terminal_router = APIRouter()

@terminal_router.websocket("/ws/terminal/{cluster_id}")
async def terminal_websocket_endpoint(
    websocket: WebSocket,
    cluster_id: str,
    db: Session = Depends(get_db)
):
    """
    Handles a WebSocket connection for an interactive terminal to a cluster.
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Authenticate the user from the token
    user = await get_current_user_from_token(token=token, db=db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Authorize: Check if the user has access to this cluster
    cluster = crud.get_cluster(db, cluster_id=cluster_id)
    if not cluster or cluster.owner.id != user.id:
        # A more robust check would also look up team membership
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Cluster not found or access denied")
        return
        
    if cluster.status != "RUNNING":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason=f"Terminal access is not available for clusters in '{cluster.status}' status.")
        return

    await websocket.accept()

    # Get the container name for the KinD cluster's control plane
    container_name = f"kind-{cluster.name}-control-plane"
    
    # Fork the process to create a child process with a pseudo-terminal (pty)
    pid, master_fd = pty.fork()

    if pid == 0:  # This is the child process
        # Execute 'docker exec' to get an interactive bash shell inside the container
        try:
            os.execvp("docker", ["docker", "exec", "-it", container_name, "bash"])
        except FileNotFoundError:
            print("ERROR: docker command not found in child process")
            os._exit(1)

    # Parent process continues here
    try:
        # Create two asyncio tasks to handle two-way data streaming
        
        # Reads from the pseudo-terminal's output and sends it to the user's websocket
        async def pty_to_ws():
            loop = asyncio.get_event_loop()
            while True:
                try:
                    data = await loop.run_in_executor(None, os.read, master_fd, 1024)
                    if not data:
                        break # pty has closed
                    await websocket.send_bytes(data)
                except (WebSocketDisconnect, OSError):
                    break

        # Reads from the user's websocket and writes it to the pseudo-terminal's input
        async def ws_to_pty():
            loop = asyncio.get_event_loop()
            while True:
                try:
                    data = await websocket.receive_bytes()
                    await loop.run_in_executor(None, os.write, master_fd, data)
                except (WebSocketDisconnect, OSError):
                    break

        # Run both tasks concurrently and wait for one to finish
        await asyncio.gather(pty_to_ws(), ws_to_pty())

    finally:
        # Cleanup: Close the file descriptor and kill the child process
        os.close(master_fd)
        try:
            os.kill(pid, 15) # Send SIGTERM
        except ProcessLookupError:
            pass # Process already exited
        print(f"Terminal session for cluster {cluster_id} closed.")
        if not websocket.client_state == WebSocketDisconnect:
            await websocket.close()