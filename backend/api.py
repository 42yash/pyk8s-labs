# backend/api.py
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import crud
import schemas
from db import get_db
from core.security import create_access_token, verify_password, get_current_user
import provisioner
import models


router = APIRouter()

@router.post("/users/register", response_model=schemas.user.User)
def register_user(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    """Handles user registration."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return crud.create_user(db=db, user=user)

@router.post("/auth/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Handles user login and returns a JWT."""
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.user.User)
def read_users_me(current_user: schemas.user.User = Depends(get_current_user)):
    """
    Fetches the profile of the currently logged-in user.
    This endpoint is protected by the get_current_user dependency.
    """
    return current_user

def run_cluster_provisioning(cluster_id: str, cluster_name: str, db: Session):
    """Background task for provisioning a cluster."""
    # Step 1: Create the cluster using KinD
    success = provisioner.create_kind_cluster(cluster_name)
    
    # Step 2: Fetch the cluster record from the DB
    db_cluster = db.query(models.cluster.Cluster).filter(models.cluster.Cluster.id == cluster_id).first()
    if not db_cluster:
        # This should rarely happen
        return 

    if success:
        # Step 3a: Get, encrypt, and store the kubeconfig
        kubeconfig = provisioner.get_kind_kubeconfig(cluster_name)
        if kubeconfig:
            db_cluster.encrypted_kubeconfig = provisioner.encrypt_data(kubeconfig)
            db_cluster.status = "RUNNING"
        else:
            db_cluster.status = "ERROR" # Failed to get kubeconfig after creation
    else:
        # Step 3b: Mark the cluster as failed
        db_cluster.status = "ERROR"

    db.commit()

def run_cluster_deletion(cluster_name: str, cluster_id: str, db: Session):
    """Background task for deleting a cluster."""
    # Step 1: Delete the KinD cluster
    provisioner.delete_kind_cluster(cluster_name)
    
    # Step 2: Remove the cluster from the database
    crud.remove_cluster(db=db, cluster_id=cluster_id)
    print(f"Cluster {cluster_name} and its database record have been deleted.")


@router.post("/clusters", response_model=schemas.cluster.Cluster, status_code=status.HTTP_202_ACCEPTED)
def create_cluster(
    cluster: schemas.cluster.ClusterCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """Creates a new KinD cluster for the user."""
    # Check if a cluster with the same name already exists for this user
    if crud.get_cluster_by_name(db, user_id=current_user.id, name=cluster.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A cluster with this name already exists.",
        )
    
    # Create the initial record in the DB
    db_cluster = crud.create_user_cluster(db=db, cluster=cluster, user_id=current_user.id)

    # Add the long-running task to the background
    background_tasks.add_task(run_cluster_provisioning, db_cluster.id, db_cluster.name, db)
    
    return db_cluster


@router.get("/clusters", response_model=list[schemas.cluster.Cluster])
def list_clusters(
    db: Session = Depends(get_db),
    current_user: models.user.User = Depends(get_current_user)
):
    """Lists all clusters for the current user."""
    return crud.get_clusters_by_user(db=db, user_id=current_user.id)

@router.delete("/clusters/{cluster_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_cluster(
    cluster_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Schedules a cluster for deletion."""
    db_cluster = crud.get_cluster(db, cluster_id=cluster_id)
    
    # Verify the cluster exists and belongs to the current user
    if not db_cluster or db_cluster.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Update status to prevent other operations
    db_cluster.status = "DELETING"
    db.commit()

    background_tasks.add_task(run_cluster_deletion, db_cluster.name, db_cluster.id, db)
    return {"message": "Cluster deletion scheduled."}