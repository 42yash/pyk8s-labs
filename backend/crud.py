# backend/crud.py

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, select
from datetime import datetime, timedelta, timezone

import models
from schemas.user import UserCreate
from schemas.cluster import ClusterCreate
from schemas.team import TeamCreate
from core.security import get_password_hash


# --- User CRUD Functions ---


def get_user(db: Session, user_id: str):
    """Fetches a user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


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


# --- Cluster CRUD Functions ---


def get_cluster_by_name(db: Session, user_id: str, name: str):
    """Fetches a cluster by name for a specific user."""
    return (
        db.query(models.Cluster)
        .filter(models.Cluster.name == name, models.Cluster.user_id == user_id)
        .first()
    )


def get_clusters_by_user(db: Session, user_id: str):
    """
    Fetches all clusters for a specific user.
    This includes clusters they own directly AND clusters owned by teams they are a member of.
    """
    user_team_ids_subquery = (
        select(models.team_memberships.c.team_id)
        .where(models.team_memberships.c.user_id == user_id)
        .scalar_subquery()
    )
    return (
        db.query(models.Cluster)
        .filter(
            or_(
                models.Cluster.user_id == user_id,
                models.Cluster.team_id.in_(user_team_ids_subquery),
            )
        )
        .all()
    )


def create_user_cluster(db: Session, cluster: ClusterCreate, user_id: str):
    """Creates the initial cluster record in the database."""
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


# --- Team CRUD Functions ---


def get_team_by_name(db: Session, name: str):
    """Fetches a team by its name."""
    return db.query(models.Team).filter(models.Team.name == name).first()


def get_team(db: Session, team_id: str):
    """Fetches a team by its ID."""
    return (
        db.query(models.Team)
        .options(joinedload(models.Team.members))
        .filter(models.Team.id == team_id)
        .first()
    )


def create_team(db: Session, team: TeamCreate, owner: models.User):
    """Creates a new team and assigns the owner as the first admin."""
    db_team = models.Team(name=team.name)
    db_team.members.append(owner)
    db.add(db_team)
    db.commit()
    stmt = (
        models.team_memberships.update()
        .where(models.team_memberships.c.team_id == db_team.id)
        .where(models.team_memberships.c.user_id == owner.id)
        .values(role="admin")
    )
    db.execute(stmt)
    db.commit()
    db.refresh(db_team)
    return db_team


def get_teams_for_user(db: Session, user_id: str):
    """Fetches all teams a user is a member of."""
    return (
        db.query(models.Team)
        .join(models.team_memberships)
        .filter(models.team_memberships.c.user_id == user_id)
        .all()
    )


def add_user_to_team(
    db: Session, team: models.Team, user: models.User, role: str = "member"
):
    """Adds a user to a team with a specific role."""
    if user in team.members:
        return team
    team.members.append(user)
    db.commit()
    stmt = (
        models.team_memberships.update()
        .where(models.team_memberships.c.team_id == team.id)
        .where(models.team_memberships.c.user_id == user.id)
        .values(role=role)
    )
    db.execute(stmt)
    db.commit()
    db.refresh(team)
    return team


def get_team_members_with_roles(db: Session, team_id: str):
    """
    Fetches all users in a team along with their roles.
    Returns a list of tuples: (User, role).
    """
    return (
        db.query(models.User, models.team_memberships.c.role)
        .join(models.team_memberships)
        .filter(models.team_memberships.c.team_id == team_id)
        .all()
    )
