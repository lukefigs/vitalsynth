
# security_config.py

from fastapi import Depends, HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.hash import argon2
from dotenv import load_dotenv
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file if present
load_dotenv(find_dotenv())

# -----------------------------
# Config
# -----------------------------
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY is not set. Check your .env file.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
API_KEY = os.getenv("VITALSYNTH_API_KEY", "dev-secret-key")
PEPPER = os.getenv("VITALSYNTH_PEPPER", "super-secret-pepper")

# -----------------------------
# Fake Admin User (dev mode)
# -----------------------------
fake_admin_user = {
    "username": "admin",
    "password_hash": argon2.hash("admin123" + PEPPER),
}

# -----------------------------
# Auth Router
# -----------------------------
admin_router = APIRouter()

@admin_router.post("/admin/token")
async def login_admin(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    if form_data.username != fake_admin_user["username"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not argon2.verify(form_data.password + PEPPER, fake_admin_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": form_data.username, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return {"access_token": token, "token_type": "bearer"}

# -----------------------------
# API Key Dependency
# -----------------------------
def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
