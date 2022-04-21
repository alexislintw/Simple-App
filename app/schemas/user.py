from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr

from app.models.user import UserSessionType


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    re_enter_password: str


class UserCreateSSO(UserBase):
    display_name: str
    is_active: bool = True
    oauth_provider: str

    class Config:
        orm_mode = True


class User(UserBase):
    id: int
    is_active: bool
    display_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserVerification(BaseModel):
    email: EmailStr


class UserPasswords(BaseModel):
    old_password: str
    new_password: str
    re_enter_new_password: str


class UserInfo(BaseModel):
    id: int
    is_active: bool
    email: EmailStr
    sign_up_at: int
    number_of_login: int
    last_user_session_at: Optional[int] = None


class UserSessionLog(BaseModel):
    id: int
    user_id: int
    user_session_type: UserSessionType
    created_at: int


class UserStatistics(BaseModel):
    total_users_sign_up: int
    total_active_sessions_today: int
    average_active_session_in_7days: float

