from datetime import timedelta
from typing import Any

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Form
from fastapi import HTTPException
from fastapi import Response
from fastapi import status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import crud
from app import models
from app import schemas
from app.core import deps 
from app.core import security
from app.core import utils
from app.core.config import settings


router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(
    response: Response,
    user: schemas.UserCreate,
    db: Session = Depends(deps.get_db)
) -> Any:
    """ Sign up with email/password
    
    註冊時，先以 get_user_by_email() 檢查該email是否已經註冊過。
    不論之前是以 email/password 方式註冊，或是以 google account 或 facebook account 註冊,
    同一個 email 不能重複註冊。
    """

    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not security.check_password_identical(user.password, user.re_enter_password):
        raise HTTPException(status_code=401, detail="Passwords are not identical")
    if not security.check_password_validated(user.password):
        raise HTTPException(status_code=402, detail="Password is not validated")
    db_user = crud.create_user(db=db, user=user)
    crud.update_user_login_count(db, user_id=db_user.id)
    crud.create_user_session_log(db, user_id=db_user.id, user_session_type=models.UserSessionType.LOGIN)

    utils.send_verification_email(user.email)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        db_user.id, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token",value=f"Bearer {access_token}", httponly=True)
    return db_user


@router.get("/", response_model=schemas.User)
def read_user(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.create_user_session_log(
        db = db, 
        user_id=current_user.id, 
        user_session_type=models.UserSessionType.READ_USER_PROFILE
    )
    return current_user


@router.get("/verify-email", response_model=schemas.User)
def verify_user_email(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    return crud.verify_user(db, user=current_user)


@router.get("/resend-email", response_model=schemas.Msg)
def resend_verification_email(
    current_user: models.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    utils.send_verification_email(current_user.email)
    return {"msg": "Email has been sent."}


@router.put("/profile", response_model=schemas.User)
def update_user_name(
    display_name: str = Form(...),
    current_user: models.User = Depends(deps.get_current_user), 
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="Email not verified")
    db_user = crud.update_user_profile(db, user=current_user, display_name=display_name)
    crud.create_user_session_log(
        db = db, 
        user_id=current_user.id, 
        user_session_type=models.UserSessionType.UPDATE_USER_PROFILE
    )
    return db_user


@router.put("/password", response_model=schemas.User)
def update_user_password(
    user_passwords: schemas.UserPasswords, 
    current_user: models.User = Depends(deps.get_current_user), 
    db: Session = Depends(deps.get_db)
) -> Any:
    if current_user is None:
        raise HTTPException(status_code=400, detail="User not found")
    if not current_user.is_active:
        raise HTTPException(status_code=401, detail="Email not verified")
    if not security.verify_password(user_passwords.old_password, current_user.hashed_password):
        raise HTTPException(status_code=402, detail="Old password is not correct")
    if not security.check_password_identical(user_passwords.new_password, user_passwords.re_enter_new_password):
        raise HTTPException(status_code=403, detail="Passwords are not identical")
    if not security.check_password_validated(user_passwords.new_password):
        raise HTTPException(status_code=404, detail="Password is invalid")
    db_user = crud.update_user_password(db, user=current_user, password=user_passwords)
    crud.create_user_session_log(
        db = db, 
        user_id=current_user.id, 
        user_session_type=models.UserSessionType.UPDATE_USER_PASSWORD
    )
    return db_user

