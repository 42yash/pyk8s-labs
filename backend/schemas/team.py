# backend/schemas/team.py
from pydantic import BaseModel, UUID4, EmailStr
from typing import List, Literal
from .user import User # Re-use the basic User schema

# --- Team Member Schemas ---

# This schema will represent a user's membership details within a team
# It extends the basic User schema with the role they have in the team.
class TeamMember(User):
    role: str

# Schema for the request body when inviting a user to a team
class TeamMemberInvite(BaseModel):
    email: EmailStr
    role: Literal['admin', 'member'] = 'member'


# --- Team Schemas ---

# Basic properties for a team
class TeamBase(BaseModel):
    name: str

# Properties needed when creating a new team
class TeamCreate(TeamBase):
    pass

# Properties to return when listing multiple teams.
# We don't need the full member list for a summary view.
class Team(TeamBase):
    id: UUID4

    class Config:
        from_attributes = True

# Properties to return for a single team's detailed view, including its members
class TeamDetails(Team):
    members: List[TeamMember] = []