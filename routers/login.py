from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from auth.security import authenticate_user, create_access_token
from schemas.user_schema import PersonLogin


loginrouter = APIRouter()


@loginrouter.post("/login/", response_model=dict[str, str])
async def login_for_access_token(
    user_data: PersonLogin,
    session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    password = user_data.password

    user = await authenticate_user(session, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "Bearer"}
