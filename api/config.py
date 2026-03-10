import os
from pathlib import Path

DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).parent.parent / "data" / "db" / "finbox.db"))

ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "change-me-to-random-secret")
ADMIN_TOKEN_EXPIRE_MINUTES = int(os.getenv("ADMIN_TOKEN_EXPIRE_MINUTES", "480"))

UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(Path(__file__).parent.parent / "data" / "uploads"))

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
