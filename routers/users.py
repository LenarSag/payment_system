from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from crud.user_repository import (
    create_person,
    delete_user,
    get_person_by_id_with_accounts,
    get_person_by_id_with_transactions,
    check_username_and_email,
    get_user_by_id,
    get_user_by_id_with_accounts,
    get_users,
    update_user
)
from db.database import get_session
from models.user import Person
from schemas.accounts_schema import UserAccount, UserTransaction
from schemas.user_schema import (
    PersonCreate, UserBase, UserWithAccounts
)
from permissions.role_based_controll import check_is_admin
from auth.security import get_current_user
from auth.pwd_crypt import get_hashed_password


usersrouter = APIRouter()


async def get_user_or_404(session: AsyncSession, id: int):
    user = await get_user_by_id(session, id)
    if not user:
        raise HTTPException(
            detail="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return user


@usersrouter.get("/", response_model=list[UserBase])
@check_is_admin
async def get_all_user(
    current_user: Annotated[Person, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    users = await get_users(session)
    return [
        UserBase(
            id=user.user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role
        )
        for user in users
    ]


@usersrouter.get("/me")
async def get_myself(
    session: AsyncSession = Depends(get_session),
    current_user: Person = Depends(get_current_user)
):
    serialized_user = UserBase(
        id=(
            current_user.admin.id
            if current_user.is_admin else current_user.user.id
        ),
        username=current_user.username,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=True
    )

    return serialized_user


@usersrouter.get("/me/accounts")
async def get_my_accounts(
    session: AsyncSession = Depends(get_session),
    current_user: Person = Depends(get_current_user)
):
    if current_user.is_admin:
        return []
    person = await get_person_by_id_with_accounts(session, current_user.id)
    serialized_accounts = [
        UserAccount(
            account_id=account.user_account_id,
            balance=account.balance
        )
        for account in person.user.accounts
    ]

    return serialized_accounts


@usersrouter.get("/me/transactions")
async def get_my_transactions(
    session: AsyncSession = Depends(get_session),
    current_user: Person = Depends(get_current_user)
):
    if current_user.is_admin:
        return []
    person = await get_person_by_id_with_transactions(
        session, current_user.id
    )
    accounts = person.user.accounts
    serialized_transactions = [
        UserTransaction(
            transaction_id=transaction.transaction_id,
            account_id=account.id,
            amount=transaction.amount,
            transaction_date=transaction.transaction_date
        )
        for account in accounts for transaction in account.transactions
    ]

    return serialized_transactions


@usersrouter.get("/{user_id}", response_model=UserWithAccounts)
@check_is_admin
async def get_user_info(
    user_id: int,
    current_user: Annotated[Person, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):

    user = await get_user_by_id_with_accounts(session, user_id)
    if user:
        serialized_user = UserWithAccounts(
            id=user.id,
            username=user.person.username,
            email=user.person.email,
            first_name=user.person.first_name,
            last_name=user.person.last_name,
            role=user.person.role,
            accounts=[
                UserAccount(
                    account_id=account.user_account_id,
                    balance=account.balance
                )
                for account in user.accounts
            ]
        )

        return serialized_user

    raise HTTPException(
        detail="User not found",
        status_code=status.HTTP_404_NOT_FOUND
    )


@usersrouter.post("/", response_class=JSONResponse)
@check_is_admin
async def create_new_user(
    new_person_data: PersonCreate,
    current_user: Annotated[Person, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):

    person = await check_username_and_email(
        session, new_person_data.username, new_person_data.email
    )
    if person:
        if person.username == new_person_data.username:
            raise HTTPException(
                detail="Username already taken",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        raise HTTPException(
            detail="Email already registered",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    hashed_password = get_hashed_password(new_person_data.password)
    new_person_data.password = hashed_password

    new_person = await create_person(session, new_person_data)

    serialized_person = UserBase(
        id=new_person.user.id,
        username=new_person.username,
        email=new_person.email,
        first_name=new_person.first_name,
        last_name=new_person.last_name,
        role=new_person.role
    )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=serialized_person.model_dump()
    )


@usersrouter.put("/{user_id}", response_model=UserBase)
@check_is_admin
async def update_user_data(
    user_id: int,
    new_person_data: PersonCreate,
    current_user: Annotated[Person, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user_to_update = await get_user_or_404(session, user_id)
    if user_to_update.person.is_admin:
        raise HTTPException(
            detail="You cant update admin",
            status_code=status.HTTP_403_FORBIDDEN
        )
    updated_user = await update_user(
        session, new_person_data, user_to_update.person
    )
    serialized_user = UserBase(
        id=updated_user.user.id,
        username=updated_user.username,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        role=updated_user.role,
        is_active=updated_user.is_active
    )
    return serialized_user


@usersrouter.delete("/{user_id}", response_class=Response)
@check_is_admin
async def delete_user_model(
    user_id: int,
    current_user: Annotated[Person, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    user_to_delete = await get_user_or_404(session, user_id)
    if user_to_delete.person.is_admin:
        raise HTTPException(
            detail="You cant delete admin",
            status_code=status.HTTP_403_FORBIDDEN
        )
    await delete_user(
        session, user_to_delete.person
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
