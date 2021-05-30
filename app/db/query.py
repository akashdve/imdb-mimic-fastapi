from typing import Optional

from fastapi import HTTPException

from app.db import DB_ENGINE
from app.models.user import UserDB, User


async def get_user(email_id: str, cls=User):
    user = await DB_ENGINE.find_one(UserDB, UserDB.email_id == email_id)
    if user is None:
        raise HTTPException(404)
    else:
        user = vars(user)
        user["is_authenticated"] = False
        user["hashed_password"] = user.get("password", "")

        user = cls(**user)

    return user
