# backend/schemas/cluster.py
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Annotated, Literal, Optional

# Properties to receive on cluster creation
class ClusterCreate(BaseModel):
    # Use Annotated to apply constraints to the 'name' field
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
    
    # TTL in hours from now
    ttl_hours: int = 1  # Default to 1 hour
    
    # Provider for the cluster
    provider: Literal['kind', 'k3d'] = 'kind'

    # Add optional team_id
    team_id: Optional[UUID4] = None


# Base properties shared by all cluster schemas
class ClusterBase(BaseModel):
    id: UUID4
    name: str
    status: str
    ttl_expires_at: datetime

# Properties to return to the client
class Cluster(ClusterBase):
    provider: str

    class Config:
        from_attributes = True