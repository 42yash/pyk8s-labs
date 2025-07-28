# backend/models/team.py
import uuid
from sqlalchemy import Column, String, UUID, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base

team_memberships = Table(
    "team_memberships",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("team_id", UUID(as_uuid=True), ForeignKey("teams.id"), primary_key=True),
    Column("role", String, default="member", nullable=False),
)


class Team(Base):
    __tablename__ = "teams"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False, unique=True)
    members = relationship("User", secondary=team_memberships, back_populates="teams")
    clusters = relationship("Cluster", back_populates="team")
