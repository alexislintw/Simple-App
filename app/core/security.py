import re
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Union
from typing import Optional

from fastapi import HTTPException
from fastapi import status
from jose import jwt
from jose import JWTError
from passlib.context import CryptContext

from app import crud
from app import models
from app import schemas
from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(db, token) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = schemas.TokenPayload(**payload)
    except JWTError:
        raise credentials_exception
    user = crud.get_user(db, user_id=token_data.sub)
    if user is None:
        raise credentials_exception
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def check_password_identical(password1,password2) -> bool:
    if password1 != password2:
        return False
    return True


def check_password_validated(password) -> bool:
    patt = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=,./?])[A-Za-z\d!@#$%^&*()_+\-=,./?]{8,}$'
    if re.search(patt,password) != None:
        return True
    return False


