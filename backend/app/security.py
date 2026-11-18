"""Password hashing and JWT helpers."""
import os
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
JWT_ALGORITHM = "HS256"

def _secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret or len(secret) < 32:
        raise RuntimeError("Set JWT_SECRET_KEY to a random value of at least 32 characters.")
    return secret

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def create_access_token(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_MINUTES", "60")))
    return jwt.encode({"sub": subject, "exp": expires}, _secret(), algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
