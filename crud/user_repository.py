from typing import Optional, Sequence
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import or_

from models.user import Person, User, Transaction, Account
from schemas.user_schema import PersonCreate


async def get_user_by_email(
    session: AsyncSession, email: EmailStr
) -> Optional[Person]:
    query = (
        select(Person).filter_by(email=email)
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_person_by_id(
    session: AsyncSession, person_id: UUID
) -> Optional[Person]:
    query = (
        select(Person)
        .filter_by(id=person_id)
        .options(selectinload(Person.user), selectinload(Person.admin))
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_id(
    session: AsyncSession, user_id: int
) -> Optional[User]:
    query = select(User).options(
        selectinload(User.person)
    ).filter_by(id=user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_user_by_id_with_accounts(
    session: AsyncSession, user_id: int
) -> Optional[User]:
    query = select(User).options(
        selectinload(User.person), selectinload(User.accounts)
    ).filter_by(id=user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_users(
    session: AsyncSession
) -> Sequence[Person]:
    query = select(Person).options(
        selectinload(Person.user)
    ).filter_by(role="user")
    result = await session.execute(query)
    return result.scalars().all()


async def get_person_by_id_with_accounts(
    session: AsyncSession, person_id: UUID
) -> Optional[Person]:
    query = (
        select(Person)
        .filter_by(id=person_id)
        .options(
            selectinload(Person.user).options(selectinload(User.accounts))
        )
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_person_by_id_with_transactions(
    session: AsyncSession, person_id: UUID
) -> Optional[Person]:
    query = (
        select(Person)
        .filter_by(id=person_id)
        .options(
            selectinload(Person.user)
            .options(
                selectinload(User.accounts)
                .options(selectinload(Account.transactions))
            )
        )
    )
    result = await session.execute(query)
    return result.scalars().first()


async def get_person_transactions(
    session: AsyncSession, person_id: UUID
) -> Sequence:
    query = (
        select(Transaction)
        .join(Transaction.account)
        .join(Account.user)
        .join(User.person)
        .where(Person.id == person_id)
    )
    result = await session.execute(query)
    return result.scalars().all()


async def check_username_and_email(
        session: AsyncSession, username: str, email: EmailStr
) -> Optional[Person]:
    query = select(Person).where(or_(
        Person.username == username, Person.email == email
    ))
    result = await session.execute(query)
    return result.scalars().first()


async def create_person(
    session: AsyncSession,
    person_data: PersonCreate
) -> Person:
    person = Person(**person_data.model_dump())
    session.add(person)
    await session.flush()

    user = User(person_id=person.id)
    session.add(user)

    await session.commit()
    await session.refresh(person, attribute_names=["user"])
    return person


async def update_user(
    session: AsyncSession,
    new_person_data: PersonCreate,
    person_to_update: Person
) -> Person:
    person_to_update.email = new_person_data.email
    person_to_update.username = new_person_data.username
    person_to_update.first_name = new_person_data.first_name
    person_to_update.last_name = new_person_data.last_name
    person_to_update.is_active = new_person_data.is_active
    await session.commit()
    await session.refresh(person_to_update, attribute_names=["user"])
    return person_to_update


async def delete_user(
    session: AsyncSession,
    person_to_delete: Person
) -> None:
    await session.delete(person_to_delete)
    await session.commit()
