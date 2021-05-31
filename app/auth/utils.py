import os
from datetime import timedelta, datetime
from typing import Optional

from fastapi import status, Header
from fastapi import Request
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.db.query import get_user
from app.models.token import TokenData
from app.models.user import User, AnonymousUser, AuthUser
from app.config import Config

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


async def authenticate_user(email_id, password):
    user = await get_user(email_id, cls=AuthUser)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    user.is_authenticated = True
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Config().SECRET_KEY, algorithm=Config.ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request, access_token: Optional[str] = Header(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = access_token
    if token is None:
        return AnonymousUser()
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError:
        # raise CustomExpiredSignatureError(status_code=status.HTTP_400_BAD_REQUEST)
        return AnonymousUser()
    except JWTError:
        raise credentials_exception

    user = await get_user(email_id=token_data.username, cls=User)

    if user is None:
        raise credentials_exception
    user.is_authenticated = True
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user is None:
        return None

    if current_user.is_anonymous:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="login required"
        )

    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user
