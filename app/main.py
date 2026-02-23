# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.exceptions.handlers import register_exception_handlers
from .routers import users as users_router
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup code
    print("Starting up...")

    # Create the async engine  and test the connection
    engine = create_async_engine(DATABASE_URL, echo=True)
    try:
        # Test the database connection
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise e

    app.state.db_session_factory = async_sessionmaker(
        bind=engine, expire_on_commit=False
    )
    yield
    # shutdown code if needed
    print("Shutting down...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router.router)
register_exception_handlers(app)
