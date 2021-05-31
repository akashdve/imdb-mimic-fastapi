from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Response, Cookie
from fastapi import status

from app.auth.utils import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.config import Config
from app.db import DB_ENGINE
from app.models.user import User, AnonymousUser, UserDB, AuthUser
from app.models.token import Token

auth_router = APIRouter()


@auth_router.get("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    return "ok"


@auth_router.post("/auth/token", response_model=Token)
async def get_token(response: Response, current_user: AuthUser):  # form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(current_user.email_id, current_user.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email_id}, expires_delta=access_token_expires
    )
    # response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/register", response_model=User)
async def register(new_user: UserDB):

    user = await DB_ENGINE.find_one(UserDB, UserDB.email_id == new_user.email_id)
    if user is None:
        new_user.password = get_password_hash(new_user.password)
        await DB_ENGINE.save(new_user)
        return User(id=str(new_user.id),
                    username=new_user.username,
                    email_id=new_user.email_id,
                    firstname=new_user.firstname,
                    lastname=new_user.lastname,
                    is_active=new_user.is_active).dict(exclude_none=True)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists!!")
