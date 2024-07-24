import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
from fastapi.exceptions import ValidationException

from config import MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH
from schemas.accounts_schema import UserAccount
from models.user import UserRoles


class PersonJWT(BaseModel):
    id: UUID


class PersonLogin(BaseModel):
    email: EmailStr
    password: str


class PersonBase(BaseModel):
    username: str = Field(
        max_length=MAX_USERNAME_LENGTH, pattern=r"^[\w.@+-]+$"
    )
    email: EmailStr = Field(max_length=MAX_EMAIL_LENGTH)
    first_name: str = Field(max_length=MAX_USERNAME_LENGTH)
    last_name: str = Field(max_length=MAX_USERNAME_LENGTH)
    role: UserRoles = Field(default=UserRoles.USER)
    is_active: bool = True

    class Config:
        from_attributes = True
        use_enum_values = True


class UserBase(PersonBase):
    id: int


class UserWithAccounts(UserBase):
    accounts: list[UserAccount]


class PersonCreate(PersonBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        password_regex = re.compile(
            r"^"
            r"(?=.*[a-z])"
            r"(?=.*[A-Z])"
            r"(?=.*\d)"
            r"(?=.*[@$!%*?&])"
            r"[A-Za-z\d@$!%*?&]"
            r"{8,}$"
        )
        if not password_regex.match(value):
            raise ValidationException(
                "Password must be at least 8 characters long, include an "
                "uppercase letter, a lowercase letter, a number, "
                "and a special character."
            )
        return value
