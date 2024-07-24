from datetime import datetime
import decimal
from enum import Enum as PyEnum
import re
import uuid

from sqlalchemy import (
    ForeignKey,
    String,
    DateTime,
    Enum,
    DECIMAL,
    func,
    UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, validates
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from config import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH


class Base(DeclarativeBase):
    pass


class UserRoles(PyEnum):
    ADMIN = "admin"
    USER = "user"


class Person(Base):
    __tablename__ = "person"

    id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(MAX_USERNAME_LENGTH), nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(MAX_EMAIL_LENGTH), unique=True
    )
    first_name: Mapped[str] = mapped_column(
        String(MAX_USERNAME_LENGTH), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(MAX_USERNAME_LENGTH), nullable=False
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles, values_callable=lambda obj: [e.value for e in obj]),
        default=UserRoles.USER.value,
        server_default=UserRoles.USER.value,
    )
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    admin: Mapped["Admin"] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @validates("username")
    def validate_username(self, key, value):
        username_regex = r"^[\w.@+-]+$"
        if not re.match(username_regex, value):
            raise ValueError("Username is invalid")
        return value

    @validates("email")
    def validate_email(self, key, value):
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise ValueError("Invalid email format")
        return value

    def __str__(self) -> str:
        return self.username

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[PG_UUID] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE")
    )

    person: Mapped["Person"] = relationship(back_populates="user")
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (UniqueConstraint("person_id"),)


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[PG_UUID] = mapped_column(
        ForeignKey("person.id", ondelete="CASCADE")
    )

    person: Mapped["Person"] = relationship(back_populates="admin")

    __table_args__ = (UniqueConstraint("person_id"),)


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    user_account_id: Mapped[int] = mapped_column(nullable=False)
    balance: Mapped[DECIMAL] = mapped_column(
        DECIMAL(precision=18, scale=2),
        nullable=False,
        default=decimal.Decimal("0.00")
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan"
    )


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[PG_UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE")
    )
    amount: Mapped[DECIMAL] = mapped_column(
        DECIMAL(precision=18, scale=2),
        nullable=False,
    )
    transaction_date: Mapped[datetime] = mapped_column(default=func.now())

    account: Mapped["Account"] = relationship(back_populates="transactions")
