import enum

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship

from app.db.session import Base


class UserSessionType(enum.Enum):
    LOGIN = 1
    LOGOUT = 2
    READ_USER_PROFILE = 3
    UPDATE_USER_PROFILE = 4
    UPDATE_USER_PASSWORD = 5


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=False)
    display_name = Column(String)
    sign_up_at = Column(Integer)
    number_of_login = Column(Integer, default=0)
    oauth_provider = Column(String, default='')


class UserSessionLog(Base):
    __tablename__ = "user_session_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_session_type = Column(Enum(UserSessionType))
    created_at = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))

