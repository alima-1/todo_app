# database.py
from fastapi.requests import Request
from sqlalchemy.orm import declarative_base


# Base class for models
# All your SQLAlchemy models will inherit from Bas
Base = declarative_base()


# Dependency to provide DB session in routes
# FastAPI can use this with Depends
async def get_session(request: Request):
    async with request.app.state.db_session_factory() as session:
        yield session
