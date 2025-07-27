# backend/models/user.py
from sqlalchemy import Column, String, UUID
from sqlalchemy.orm import relationship # Import relationship
import uuid
from .base import Base
from .team import team_memberships # Import the association table

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # This defines the one-to-many relationship from the User side
    clusters = relationship("Cluster", back_populates="owner")
    
    # Relationship to the Team model through the association table
    teams = relationship(
        "Team",
        secondary=team_memberships,
        back_populates="members"
    )