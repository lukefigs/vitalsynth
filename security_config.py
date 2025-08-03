
# security_config.py

from fastapi import Depends, HTTPException, status, APIRouter, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.hash import argon2
import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file if present
load_dotenv(find_dotenv())

# -----------------------------
# Config
# -----------------------------
SECRET_KEY = os.getenv("MODEL_AES_KEY", "fallback-secret-key")
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
def login_admin(
    username: str = Form(...),
    password: str = Form(...)
):
    if username != fake_admin_user["username"]:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not argon2.verify(password + PEPPER, fake_admin_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode(
        {"sub": username, "exp": expire},
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
