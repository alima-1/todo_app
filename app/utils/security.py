# app/utils/security.py
from passlib.context import CryptContext
import re
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from httpx import AsyncClient

# Load environment variables from .env file
load_dotenv()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def is_strong_password(password: str) -> bool:
    """Check if the password meets strength requirements."""
    if (len(password) < 8 or
            not re.search(r"[A-Z]", password) or
            not re.search(r"[a-z]", password) or
            not re.search(r"[0-9]", password) or
            not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
        return False
    return True


# secret key for JWT encoding/decoding (from environment variable)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
# algorithm used for JWT
ALGORITHM = "HS256"


def create_email_verification_token(user_id: int) -> str:
    """Create a JWT token for email verification."""
    payload = {
        "user_id": user_id,
        "exp": datetime.now() + timedelta(hours=24),  # token expires in 24 hours
        "purpose": "email_verification"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_email_verification_token(token: str) -> int:
    """Decode a JWT token and return the user ID if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("purpose") != "email_verification":
            raise jwt.InvalidTokenError
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid token signature")


def create_vefication_link(token: str) -> str:
    """Create a verification link for the user to click."""
    return f"http://localhost:8000/verify-email?token={token}"


async def send_verification_email(email: str, verification_link: str):
    url = "https://sandbox.api.mailtrap.io/api/send"
    headers = {
        "Api-Token": os.getenv("MAILTRAP_API_TOKEN"),
        "Content-Type": "application/json"
    }
    payload = {
        "from": {
            "email": "verify@demomailtrap.co",
            "name": "Task Management App"
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Verify your email",
        "html": (
            f"<p>Please click the link to verify your email: "
            f"<a href='{verification_link}'>Verify Email</a></p>"
        )
    }
    async with AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()  # raise an error for bad response
