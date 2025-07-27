import json
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, WebSocket, WebSocketDisconnect, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import crud
import schemas
from schemas.team import TeamCreate, Team, TeamDetails, TeamMemberInvite, TeamMember
from db import get_db, SessionLocal
from core.security import create_access_token, verify_password, get_current_user, require_team_role
import provisioner
import models
from redis_client import get_redis_connection
from websocket_manager import manager, get_current_user_from_token, REDIS_CHANNEL


router = APIRouter()
teams_router = APIRouter()

# --- RBAC Dependency Instances ---
require_admin = require_team_role(allowed_roles=["admin"])
require_member = require_team_role(allowed_roles=["admin", "member"])


# --- USER/AUTH ENDPOINTS ---
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

# --- BACKGROUND TASKS ---
async def run_cluster_provisioning(cluster_id: str, cluster_name: str, user_id: str, provider: str):
    db = SessionLocal()
    try:
        success = await asyncio.to_thread(provisioner.create_cluster, cluster_name, provider)
        
        db_cluster = db.query(models.cluster.Cluster).filter(models.cluster.Cluster.id == cluster_id).first()
        if not db_cluster: return 
        
        new_status = ""
        if success:
            kubeconfig = await asyncio.to_thread(provisioner.get_kubeconfig, cluster_name, provider)
            
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
    db = SessionLocal()
    try:
        # Fetch the cluster from DB to get its provider
        db_cluster = crud.get_cluster(db, cluster_id)
        if not db_cluster:
            print(f"Cluster with ID {cluster_id} not found for deletion task.")
            return

        await asyncio.to_thread(provisioner.delete_cluster, cluster_name, db_cluster.provider)
        
        await publish_status_update(user_id=user_id, cluster_id=cluster_id, status="DELETED")
        crud.remove_cluster(db=db, cluster_id=cluster_id)
        print(f"Cluster {cluster_name} and its database record have been deleted.")
    finally:
        db.close()

# --- CLUSTER API ENDPOINTS ---
@router.post("/clusters", response_model=schemas.cluster.Cluster, status_code=status.HTTP_202_ACCEPTED)
async def create_cluster(cluster: schemas.cluster.ClusterCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    if crud.get_cluster_by_name(db, user_id=current_user.id, name=cluster.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A cluster with this name already exists.")
        
    db_cluster = crud.create_user_cluster(db=db, cluster=cluster, user_id=current_user.id)
    
    await publish_status_update(user_id=str(current_user.id), cluster_id=str(db_cluster.id), status="PROVISIONING")
    
    background_tasks.add_task(run_cluster_provisioning, db_cluster.id, db_cluster.name, str(current_user.id), db_cluster.provider)
    
    return db_cluster

@router.get("/clusters", response_model=list[schemas.cluster.Cluster])
def list_clusters(db: Session = Depends(get_db), current_user: models.user.User = Depends(get_current_user)):
    return crud.get_clusters_by_user(db=db, user_id=current_user.id)

@router.get("/clusters/{cluster_id}/kubeconfig", response_class=Response)
def get_cluster_kubeconfig(
    cluster_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_cluster = crud.get_cluster(db, cluster_id=cluster_id)
    
    if not db_cluster or db_cluster.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")

    if db_cluster.status != "RUNNING":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Kubeconfig is not available for clusters in '{db_cluster.status}' status.")
        
    if not db_cluster.encrypted_kubeconfig:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kubeconfig not found for this cluster.")

    try:
        decrypted_kubeconfig = provisioner.decrypt_data(db_cluster.encrypted_kubeconfig)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to decrypt kubeconfig.")

    return Response(content=decrypted_kubeconfig, media_type="text/plain")

@router.delete("/clusters/{cluster_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_cluster(cluster_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_cluster = crud.get_cluster(db, cluster_id=cluster_id)
    if not db_cluster or db_cluster.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db_cluster.status = "DELETING"
    db.commit()
    await publish_status_update(user_id=str(current_user.id), cluster_id=str(db_cluster.id), status="DELETING")
    background_tasks.add_task(run_cluster_deletion, db_cluster.name, db_cluster.id, str(current_user.id))
    return {"message": "Cluster deletion scheduled."}

# --- TEAM API ENDPOINTS ---

@teams_router.post("", response_model=Team, status_code=status.HTTP_201_CREATED)
def create_new_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if crud.get_team_by_name(db, name=team.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A team with this name already exists.")
    
    db_team = crud.create_team(db=db, team=team, owner=current_user)
    return db_team

@teams_router.get("", response_model=list[Team])
def list_user_teams(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_teams_for_user(db=db, user_id=current_user.id)

@teams_router.get("/{team_id}", response_model=TeamDetails, dependencies=[Depends(require_member)])
def get_team_details(
    team_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_team = crud.get_team(db, team_id=team_id)
    
    members_with_roles = crud.get_team_members_with_roles(db, team_id=team_id)
    
    team_details = TeamDetails(
        id=db_team.id,
        name=db_team.name,
        members=[
            TeamMember(id=user.id, email=user.email, role=role)
            for user, role in members_with_roles
        ]
    )
    return team_details

@teams_router.post("/{team_id}/members", response_model=TeamDetails, dependencies=[Depends(require_admin)])
def invite_member_to_team(
    team_id: str,
    invite: TeamMemberInvite,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    db_team = crud.get_team(db, team_id=team_id)

    user_to_add = crud.get_user_by_email(db, email=invite.email)
    if not user_to_add:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with email {invite.email} not found.")

    if user_to_add in db_team.members:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already a member of this team.")
        
    crud.add_user_to_team(db=db, team=db_team, user=user_to_add, role=invite.role)
    
    return get_team_details(team_id=team_id, db=db, current_user=current_user)


# --- WEBSOCKET ENDPOINT ---
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


# Include the new team router in the main API router
router.include_router(teams_router, prefix="/teams", tags=["teams"])