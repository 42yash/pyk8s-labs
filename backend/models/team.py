# backend/models/team.py
import uuid
from sqlalchemy import Column, String, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base

# Association Table for the many-to-many relationship between users and teams
team_memberships = Table(
    "team_memberships",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("team_id", UUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True),
    Column("role", String, default="member", nullable=False) # e.g., 'admin', 'member'
)

class Team(Base):
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False, unique=True)

    # Relationship to the User model through the association table
    members = relationship(
        "User",
        secondary=team_memberships,
        back_populates="teams"
    )
    
    # Relationship to the Cluster model
    clusters = relationship("Cluster", back_populates="team")