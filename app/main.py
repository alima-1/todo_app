# main.py
from fastapi import FastAPI
from .models import *
from .database import engine, Base
from .routers import users as users_router

app = FastAPI()
app.include_router(users_router.router)


# Async table creation
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
