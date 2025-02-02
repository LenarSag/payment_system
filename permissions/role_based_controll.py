from functools import wraps

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_session
from models.user import Person
from auth.security import get_current_user


def check_is_admin(func):
    """Checks if current user has admin rights."""
    @wraps(func)
    async def wrapper(
        *args,
        current_user: Person = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
        **kwargs
    ):
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return await func(
            *args, current_user=current_user, session=session, **kwargs
        )
    return wrapper
