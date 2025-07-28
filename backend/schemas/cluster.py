# backend/schemas/cluster.py
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Annotated, Literal, Optional


class ClusterCreate(BaseModel):
    name: Annotated[
        str,
        Field(
            strip_whitespace=True,
            to_lower=True,
            min_length=3,
            max_length=50,
            pattern=r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$",
        ),
    ]
    ttl_hours: int = 1
    provider: Literal["kind", "k3d"] = "kind"
    team_id: Optional[UUID4] = None


class ClusterBase(BaseModel):
    id: UUID4
    name: str
    status: str
    ttl_expires_at: datetime


class Cluster(ClusterBase):
    provider: str

    class Config:
        from_attributes = True
