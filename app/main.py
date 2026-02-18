# main.py
from fastapi import FastAPI

from app.exceptions.handlers import register_exception_handlers
from .models import *
from .database import engine, Base
from .routers import users as users_router

app = FastAPI()
app.include_router(users_router.router)
register_exception_handlers(app)

# Async table creation
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
