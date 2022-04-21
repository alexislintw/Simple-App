from datetime import timedelta
from enum import Enum
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import RedirectResponse
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO
from sqlalchemy.orm import Session
from starlette.requests import Request

from app import crud
from app import models
from app import schemas
from app.core import deps 
from app.core import security
from app.core import utils
from app.core.config import settings
from app.core.config import ErrorMessage
from app.core.config import OauthProvider
from app.core.config import OauthAction


router = APIRouter()


def create_sso(provider: OauthProvider, action: OauthAction) -> [GoogleSSO, FacebookSSO]:
    path = '/third-party-oauth2/' + provider + '/' + action + '/auth'
    if provider == OauthProvider.GOOGLE.value:
        return GoogleSSO(
            settings.GOOGLE_CLIENT_ID, 
            settings.GOOGLE_CLIENT_SECRET, 
            settings.SERVER_HOST + path)
    elif provider == OauthProvider.FACEBOOK.value:
        return FacebookSSO(
            settings.FACEBOOK_CLIENT_ID, 
            settings.FACEBOOK_CLIENT_SECRET, 
            settings.SERVER_HOST + path)


@router.get("/{provider}/{action}", include_in_schema=False)
async def third_party_login(provider: OauthProvider, action: OauthAction):
    sso = create_sso(provider, action)
    return await sso.get_login_redirect()


@router.get("/{provider}/register/auth", 
    response_class=RedirectResponse, 
    include_in_schema=False
)
async def third_parth_register_callback(
    provider: OauthProvider, 
    request: Request, 
    db: Session = Depends(deps.get_db)
):
    """ Sign up with third party account

    註冊時，先以 get_user_by_email() 檢查該email是否已經註冊過。
    不論之前是以 google account 或 facebook account 註冊,  或是以 email/password 方式註冊，
    同一個 email 不能重複註冊。
    """

    sso = create_sso(provider, OauthAction.REGISTER.value)
    sso_user = await sso.verify_and_process(request)
    if not sso_user:
        return RedirectResponse(
            settings.EXCEPT_REDIRECT_URL+\
            "?msg="+str(ErrorMessage.AUTHENTICATION_FAILED.value)
        )
    db_user = crud.get_user_by_email(db, email=sso_user.email)
    if db_user:
        return RedirectResponse(
            settings.EXCEPT_REDIRECT_URL+\
            "?msg="+str(ErrorMessage.EMAIL_ALREADY_EXISTS.value)
        )
    user = schemas.UserCreateSSO(
        email = sso_user.email,
        display_name = sso_user.display_name,
        is_active = True,
        oauth_provider = provider,
    )
    db_user = crud.create_user_with_sso(db=db, user=user)
    crud.update_user_login_count(db, user_id=db_user.id)
    crud.create_user_session_log(db, user_id=db_user.id, user_session_type=models.UserSessionType.LOGIN)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        db_user.id, expires_delta=access_token_expires
    )    
    response = RedirectResponse(settings.SSO_REDIRECT_URL)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True
    )
    return response


@router.get("/{provider}/login/auth", 
    response_class=RedirectResponse, 
    include_in_schema=False
)
async def third_parth_login_callback(
    provider: OauthProvider, 
    request: Request, 
    db: Session = Depends(deps.get_db)
):
    """ Sign in with third party account
    
    登入時，先以 get_user_by_email_and_provider() 檢查該 email 是否已註冊。
    必須先以該 google account 或 facebook account 註冊過才能登入。
    先前以 email/password 方式註冊的，不能用這個方式登入。
    """

    sso = create_sso(provider, OauthAction.LOGIN.value)
    sso_user = await sso.verify_and_process(request)
    if not sso_user:
        return RedirectResponse(
            settings.EXCEPT_REDIRECT_URL+\
            "?msg="+str(ErrorMessage.AUTHENTICATION_FAILED.value)
        )
    db_user = crud.get_user_by_email_and_provider(db, email=sso_user.email, oauth_provider=provider)
    if not db_user:
        return RedirectResponse(
            settings.EXCEPT_REDIRECT_URL+\
            "?msg="+str(ErrorMessage.ACCOUNT_NOT_REGISTERED.value)
        )
    crud.update_user_login_count(db, user_id=db_user.id)
    crud.create_user_session_log(db, user_id=db_user.id, user_session_type=models.UserSessionType.LOGIN)
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        db_user.id, expires_delta=access_token_expires
    )
    response = RedirectResponse(settings.SSO_REDIRECT_URL)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True
    )
    return response

