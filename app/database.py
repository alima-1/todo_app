# database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the async engine
# The engine manages the connection pool to PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory
# SessionLocal will be used in routes to get a session
asyns_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Base class for models
# All your SQLAlchemy models will inherit from Base
Base = declarative_base()


# Dependency to provide DB session in routes
# FastAPI can use this with Depends
async def get_session():
    async with asyns_session() as session:
        yield session
