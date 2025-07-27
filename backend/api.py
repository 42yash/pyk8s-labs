# backend/api.py
import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import crud
import schemas
from db import get_db, SessionLocal # Import SessionLocal
from core.security import create_access_token, verify_password, get_current_user
import provisioner
import models
from redis_client import get_redis_connection
from websocket_manager import manager, get_current_user_from_token, REDIS_CHANNEL


router = APIRouter()

async def publish_status_update(user_id: str, cluster_id: str, status: str):
    """Publishes a cluster status update to the Redis Pub/Sub channel."""
    redis_conn = get_redis_connection()
    message = json.dumps({
        "user_id": str(user_id),
        "cluster_id": str(cluster_id),
        "status": status
    })
    await redis_conn.publish(REDIS_CHANNEL, message)

# --- START: USER/AUTH ENDPOINTS (No Changes) ---
@router.post("/users/register", response_model=schemas.user.User)
def register_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/auth/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(data={"sub": user.email})
    user_schema = schemas.user.User.from_orm(user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_schema}

@router.get("/users/me", response_model=schemas.user.User)
def read_users_me(current_user: schemas.user.User = Depends(get_current_user)):
    return current_user
# --- END: USER/AUTH ENDPOINTS ---


# --- START: CORRECTED BACKGROUND TASKS ---
async def run_cluster_provisioning(cluster_id: str, cluster_name: str, user_id: str):
    """Background task for provisioning a cluster. Manages its own DB session."""
    db = SessionLocal()
    try:
        success = provisioner.create_kind_cluster(cluster_name)
        
        db_cluster = db.query(models.cluster.Cluster).filter(models.cluster.Cluster.id == cluster_id).first()
        if not db_cluster:
            return 

        new_status = ""
        if success:
            kubeconfig = provisioner.get_kind_kubeconfig(cluster_name)
            if kubeconfig:
                db_cluster.encrypted_kubeconfig = provisioner.encrypt_data(kubeconfig)
                new_status = "RUNNING"
            else:
                new_status = "ERROR"
        else:
            new_status = "ERROR"

        db_cluster.status = new_status
        db.commit()
        await publish_status_update(user_id=user_id, cluster_id=str(cluster_id), status=new_status)
    finally:
        db.close()


async def run_cluster_deletion(cluster_name: str, cluster_id: str, user_id: str):
    """Background task for deleting a cluster. Manages its own DB session."""
    db = SessionLocal()
    try:
        provisioner.delete_kind_cluster(cluster_name)
        await publish_status_update(user_id=user_id, cluster_id=cluster_id, status="DELETED")
        crud.remove_cluster(db=db, cluster_id=cluster_id)
        print(f"Cluster {cluster_name} and its database record have been deleted.")
    finally:
        db.close()
# --- END: CORRECTED BACKGROUND TASKS ---


# --- START: CLUSTER API ENDPOINTS (Updated to not pass DB to tasks) ---
@router.post("/clusters", response_model=schemas.cluster.Cluster, status_code=status.HTTP_202_ACCEPTED)
async def create_cluster(
    cluster: schemas.cluster.ClusterCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    if crud.get_cluster_by_name(db, user_id=current_user.id, name=cluster.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A cluster with this name already exists.")
    
    db_cluster = crud.create_user_cluster(db=db, cluster=cluster, user_id=current_user.id)
    
    await publish_status_update(user_id=str(current_user.id), cluster_id=str(db_cluster.id), status="PROVISIONING")
    
    # The 'db' argument is no longer passed to the background task
    background_tasks.add_task(run_cluster_provisioning, db_cluster.id, db_cluster.name, str(current_user.id))
    
    return db_cluster

@router.get("/clusters", response_model=list[schemas.cluster.Cluster])
def list_clusters(db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    return crud.get_clusters_by_user(db=db, user_id=current_user.id)

@router.delete("/clusters/{cluster_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_cluster(
    cluster_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_cluster = crud.get_cluster(db, cluster_id=cluster_id)
    
    if not db_cluster or db_cluster.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cluster not found")

    db_cluster.status = "DELETING"
    db.commit()

    await publish_status_update(user_id=str(current_user.id), cluster_id=str(db_cluster.id), status="DELETING")

    # The 'db' argument is no longer passed to the background task
    background_tasks.add_task(run_cluster_deletion, db_cluster.name, db_cluster.id, str(current_user.id))
    return {"message": "Cluster deletion scheduled."}
# --- END: CLUSTER API ENDPOINTS ---

# --- START: WEBSOCKET ENDPOINT (No Changes) ---
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    user = await get_current_user_from_token(token=token, db=db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = str(user.id)
    await manager.connect(websocket, user_id)
    print(f"WebSocket connected for user: {user.email} (ID: {user_id})")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"WebSocket disconnected for user: {user.email} (ID: {user_id})")
# --- END: WEBSOCKET ENDPOINT ---