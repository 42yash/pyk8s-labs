# backend/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

import crud
import models
from core.config import settings
from db import get_db
from schemas.user import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    """
    Dependency to get the current user from a JWT token.
    Decodes the token, validates the signature, and fetches the user from the DB.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# --- NEW RBAC DEPENDENCY ---

def require_team_role(allowed_roles: List[str]):
    """
    Dependency factory to check if a user has a specific role within a team.
    """
    def _check_role(
        team_id: str,
        current_user: models.User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        """
        The actual dependency that will be injected into the endpoint.
        """
        user_role_tuple = (
            db.query(models.team_memberships.c.role)
            .filter(
                models.team_memberships.c.user_id == current_user.id,
                models.team_memberships.c.team_id == team_id,
            )
            .first()
        )

        # If user is not a member, they won't have a role
        if not user_role_tuple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found or you are not a member.",
            )
        
        user_role = user_role_tuple[0]

        # Check if their role is one of the allowed roles
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        
        return user_role # Return the role for potential use in the endpoint

    return _check_role
# --- END NEW RBAC DEPENDENCY ---