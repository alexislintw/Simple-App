from datetime import date
from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app import models
from app import schemas
from app.db.session import engine


def get_user_info_list(db: Session, skip: int = 0, limit: int = 100):
    """ Get a list of all users that have signed up."""

    sql = ("SELECT users.id, users.email, users.is_active, users.sign_up_at, "
        "users.number_of_login, (SELECT created_at from user_session_logs as t "
        "where t.user_id=users.id ORDER BY t.id DESC LIMIT 1) as created_at "
        "FROM users LIMIT " + str(skip) + ", " + str(limit))
    results = db.execute(sql)
    return [
        schemas.UserInfo(id=row.id, email=row.email, is_active=row.is_active, 
            sign_up_at=row.sign_up_at, number_of_login=row.number_of_login, 
            last_user_session_at=row.created_at
        ) for row in results
    ]


def get_user_sign_up_count(db: Session) -> int:
    """ Get total number of users signed up. """

    count = db.query(func.count(models.User.id)).scalar()
    return count


def get_active_user_session_count(db: Session, n_days: int = 1) -> float:
    """ Average number of active session users in the last n days rolling."""

    ONE_DAY_SECONDS = 86400
    today = date.today()
    midnight = datetime.combine(today, datetime.min.time())
    midnight_timestamp = midnight.timestamp()
    n_days_ago_timestamp = midnight_timestamp - ONE_DAY_SECONDS*(n_days-1)

    conn = engine.connect()
    sql = ("SELECT user_id,created_at FROM user_session_logs WHERE created_at > "
        + str(n_days_ago_timestamp))
    df = pd.read_sql(sql, conn)
    total_seconds = df['created_at'] - n_days_ago_timestamp
    df['day'] = np.ceil(total_seconds / ONE_DAY_SECONDS).astype(int)
    return np.mean([df[df['day']==(n+1)].user_id.nunique() for n in range(n_days)])

