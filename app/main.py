# main.py
from fastapi import FastAPI
from .models import users
from .database import engine

app = FastAPI()


# Async table creation
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(users.Base.metadata.create_all)
