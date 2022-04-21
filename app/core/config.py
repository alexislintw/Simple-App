import os
from enum import Enum
from typing import List

from pydantic import AnyHttpUrl
from pydantic import BaseSettings
from pydantic import EmailStr


class ErrorMessage(Enum):
    AUTHENTICATION_FAILED = 1
    EMAIL_ALREADY_EXISTS = 2
    ACCOUNT_NOT_REGISTERED = 3


class OauthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"


class OauthAction(str, Enum):
    REGISTER = "register"
    LOGIN = "login"


class Settings(BaseSettings):
    SECRET_KEY = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3
    SERVER_HOST: AnyHttpUrl = "https://simple-app-420.herokuapp.com"

    TEMPLATE_DIR = "app/templates"
    STATIC_FILES_PATH = "/static"
    ALGORITHM = "HS256"

    SQLALCHEMY_DATABASE_URL = "sqlite:///./app/db/sql_app.db"

    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
    EMAIL_TEMPLATE = "app/templates/new_account.html"    
    EMAIL_ADMIN_USER: EmailStr = "alexisyclin@gmail.com"
    EMAIL_SUBJECT = "[Simple App] verification email"
    
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
    FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

    SSO_REDIRECT_URL = STATIC_FILES_PATH + "/single_page.htm"
    EXCEPT_REDIRECT_URL = STATIC_FILES_PATH + "/exception.htm"

    class Config:
        case_sensitive = True


settings = Settings()
