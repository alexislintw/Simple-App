from datetime import timedelta
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import crud
from app import models
from app import schemas
from app.core import deps
from app.core import security
from app.core.config import settings


router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_with_email_and_password(
    response: Response, 
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """ Sign in with email/password

    登入時，先以 get_user_by_email_and_provider() 檢查該 email 是否已註冊。
    必須先以該 email/password 註冊過才能登入。
    先前若是以 google oauth 或 facebook oauth 方式註冊的，不能用這個方式登入。
    """

    user = crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.update_user_login_count(db, user_id=user.id)
    crud.create_user_session_log(db, user_id=user.id, user_session_type=models.UserSessionType.LOGIN)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/logout", response_model=schemas.Msg)
def logout(
    response: Response, 
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    crud.create_user_session_log(db, user_id=current_user.id, user_session_type=models.UserSessionType.LOGOUT)
    
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    return {"msg": "success"}

