# backend/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4

# Properties to receive via API on user creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Properties to return via API, hiding the password
class User(BaseModel):
    id: UUID4
    email: EmailStr

    class Config:
        # This allows Pydantic to read data from ORM models
        from_attributes = True


class TokenData(BaseModel):
    email: Optional[str] = None