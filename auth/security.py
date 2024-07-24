from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

import config as config
from crud.user_repository import get_person_by_id, get_user_by_email
from db.database import get_session
from models.user import Person
from auth.pwd_crypt import verify_password
from schemas.user_schema import PersonJWT


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticate_user(
    session: AsyncSession, email: EmailStr, password: str
):
    user = await get_user_by_email(session, email)
    if not user or not verify_password(password, user.password):
        return None
    return user


def create_access_token(person: Person) -> str:
    to_encode = {"sub": str(person.id)}
    expire = datetime.now() + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


def get_user_from_token(
    token: str = Depends(oauth2_scheme)
) -> Optional[PersonJWT]:
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        return PersonJWT(
            id=payload.get("sub"),
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    user_data: PersonJWT = Depends(get_user_from_token)
) -> Optional[Person]:
    user = await get_person_by_id(session, user_data.id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized, could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
