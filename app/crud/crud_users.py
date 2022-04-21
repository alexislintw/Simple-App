import time
from typing import Optional
from typing import List

from pydantic import EmailStr
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app.core import security
from app.core.config import OauthProvider


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_obj = models.User(
        email=user.email,
        hashed_password=security.get_password_hash(user.password),
        sign_up_at=time.time()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_user_with_sso(db: Session, user: schemas.UserCreateSSO) -> models.User:
    db_obj = models.User(
        email=user.email,
        display_name=user.display_name,
        is_active=user.is_active,
        sign_up_at=time.time(),
        oauth_provider=user.oauth_provider,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    #user = get_user_by_email(db, email=email)
    user = get_user_by_email_and_provider(db, email=email, oauth_provider='')
    if not user:
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    return user


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: EmailStr) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_email_and_provider(db, email: EmailStr, oauth_provider: OauthProvider):
    return db.query(models.User).filter(
        models.User.email == email, 
        models.User.oauth_provider == oauth_provider
        ).first()


def verify_user(db: Session, user: models.User) -> models.User:
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def update_user_profile(
    db: Session, user: models.User, display_name: str
) -> Optional[models.User]: 
    user.display_name = display_name
    db.commit()
    db.refresh(user)
    return user


def update_user_password(
    db: Session, user: models.User, password: schemas.UserPasswords
) -> Optional[models.User]:
    user.hashed_password = security.get_password_hash(password.new_password)
    db.commit()
    db.refresh(user)
    return user


def update_user_login_count(db: Session, user_id: int) -> Optional[models.User]:
    db_obj = db.query(models.User).filter(models.User.id == user_id).first()
    db_obj.number_of_login += 1
    db.commit()
    db.refresh(db_obj)
    return db_obj


def create_user_session_log(
    db: Session, user_id: int, user_session_type: models.UserSessionType
) -> Optional[models.UserSessionLog]:
    db_obj = models.UserSessionLog(
        user_id=user_id,
        user_session_type=user_session_type,
        created_at=time.time()
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

