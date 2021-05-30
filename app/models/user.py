from datetime import datetime
from typing import Optional, Any, Union

from pydantic import BaseModel, validator
from odmantic import Model, ObjectId


class UserDB(Model):
    __collection__ = "user"

    username: str
    email_id: str
    password: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    modified_at: datetime = datetime.utcnow()

    @validator("email_id", "password")
    def never_empty(cls, s: str):
        if len(s) > 0:
            return s
        else:
            raise ValueError("Value cannot be an empty string")


class User(BaseModel):
    id: Union[str, ObjectId] = None
    username: Optional[str] = None
    email_id: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    is_active: bool = True
    is_authenticated: Optional[bool] = None
    is_anonymous: Optional[bool] = None


class AuthUser(User):
    password: str = None


class AnonymousUser(User):
    # id: int = -1
    username: str = ""
    email_id: str = ""
    is_active: bool = False
    is_authenticated: bool = False
    is_anonymous: bool = True
