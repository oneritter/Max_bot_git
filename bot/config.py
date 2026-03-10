import os
from pathlib import Path

MAX_BOT_TOKEN = os.getenv("MAX_BOT_TOKEN", "")

DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).parent.parent / "data" / "db" / "finbox.db"))

GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "")
GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
GOOGLE_SHEETS_SHEET_NAME = os.getenv("GOOGLE_SHEETS_SHEET_NAME", "Лист1")

UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(Path(__file__).parent.parent / "data" / "uploads"))
