# backend/models/cluster.py
import uuid
from sqlalchemy import Column, String, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class Cluster(Base):
    __tablename__ = "clusters"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    status = Column(String, nullable=False)
    provider = Column(String, nullable=False, default="kind")
    encrypted_kubeconfig = Column(String, nullable=True)
    ttl_expires_at = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)
    owner = relationship("User", back_populates="clusters")
    team = relationship("Team", back_populates="clusters")
