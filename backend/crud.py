# backend/crud.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

import models
from schemas.user import UserCreate
from schemas.cluster import ClusterCreate
from core.security import get_password_hash


def get_user_by_email(db: Session, email: str):
    """Fetches a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: UserCreate):
    """Creates a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_cluster_by_name(db: Session, user_id: str, name: str):
    """Fetches a cluster by name for a specific user."""
    return (
        db.query(models.Cluster)
        .filter(models.Cluster.name == name, models.Cluster.user_id == user_id)
        .first()
    )


def get_clusters_by_user(db: Session, user_id: str):
    """Fetches all clusters for a specific user."""
    return db.query(models.Cluster).filter(models.Cluster.user_id == user_id).all()


def create_user_cluster(db: Session, cluster: ClusterCreate, user_id: str):
    """Creates the initial cluster record in the database."""
    # Calculate the expiration time
    ttl_delta = timedelta(hours=cluster.ttl_hours)
    expires_at = datetime.now(timezone.utc) + ttl_delta

    db_cluster = models.Cluster(
        name=cluster.name,
        user_id=user_id,
        status="PROVISIONING",
        ttl_expires_at=expires_at,
        provider=cluster.provider,
        team_id=cluster.team_id,
    )
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster


def get_cluster(db: Session, cluster_id: str):
    """Fetches a single cluster by its ID."""
    return db.query(models.Cluster).filter(models.Cluster.id == cluster_id).first()


def get_expired_clusters(db: Session):
    """Fetches all clusters whose TTL has expired."""
    return (
        db.query(models.Cluster)
        .filter(models.Cluster.ttl_expires_at <= datetime.now(timezone.utc))
        .all()
    )


def remove_cluster(db: Session, cluster_id: str):
    """Removes a cluster record from the database."""
    db_cluster = (
        db.query(models.Cluster).filter(models.Cluster.id == cluster_id).first()
    )
    if db_cluster:
        db.delete(db_cluster)
        db.commit()
    return db_cluster
