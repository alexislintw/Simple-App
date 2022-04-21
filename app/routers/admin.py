from typing import Any
from typing import List

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app import crud
from app import schemas
from app.core import deps


router = APIRouter()


@router.get("/user-info-list", response_model=List[schemas.UserInfo])
def read_user_info_list(
    db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100
) -> Any:
    users = crud.get_user_info_list(db, skip=skip, limit=limit)
    return users


@router.get("/statistics", response_model=schemas.UserStatistics)
def read_user_statistics(db: Session = Depends(deps.get_db)) -> Any:
    return {
        'total_users_sign_up': crud.get_user_sign_up_count(db),
        'total_active_sessions_today': crud.get_active_user_session_count(db,1),
        'average_active_session_in_7days': round(crud.get_active_user_session_count(db,7), 2)
    }


