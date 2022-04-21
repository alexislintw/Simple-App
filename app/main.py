from fastapi import FastAPI
from fastapi import Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.routers import admin
from app.routers import login
from app.routers import third_party_oauth2
from app.routers import users
from app.core.config import settings
from app.db.session import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(login.router, tags=["login"])
app.include_router(third_party_oauth2.router, prefix="/third-party-oauth2", tags=["third_party_oauth2"])
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
async def root():
    return RedirectResponse(
        url = "/static/index.htm", 
        status_code=303
    )

