# backend/models/cluster.py

import uuid
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base

class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False) # e.g., "PROVISIONING", "RUNNING", "ERROR"
    provider = Column(String, nullable=False, default='kind') # Add provider field

    # This will store the kubeconfig, encrypted
    encrypted_kubeconfig = Column(String, nullable=True)
    
    # Time-To-Live (TTL) expiration timestamp
    ttl_expires_at = Column(DateTime(timezone=True), nullable=False)

    # Foreign Key to link with the user who owns this cluster
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Foreign Key to link with the team that owns this cluster (optional)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)


    # This creates a back-reference so we can access user.clusters
    owner = relationship("User", back_populates="clusters")
    
    # This creates a back-reference so we can access team.clusters
    team = relationship("Team", back_populates="clusters")