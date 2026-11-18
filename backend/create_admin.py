"""Create the first AgriVision AI administrator from environment variables.

Run from the backend directory after configuring .env:
    python create_admin.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from sqlalchemy import inspect

from app.database import SessionLocal, engine
from app.models import User
from app.security import hash_password

def main() -> None:
    full_name = os.getenv("ADMIN_FULL_NAME", "").strip()
    email = os.getenv("ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD", "")

    if not full_name or not email or len(password) < 12:
        raise SystemExit("Set ADMIN_FULL_NAME, ADMIN_EMAIL, and an ADMIN_PASSWORD of at least 12 characters in backend/.env.")

    if not inspect(engine).has_table('users'):
        raise SystemExit("Database tables are missing. Run 'python -m alembic upgrade head' first.")
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise SystemExit("An account with this email already exists. No account or password was changed.")
        admin = User(full_name=full_name, email=email, password_hash=hash_password(password), role='admin')
        db.add(admin)
        db.commit()
        print(f"Administrator account created for {email}.")
    finally:
        db.close()

if __name__ == "__main__":
    main()