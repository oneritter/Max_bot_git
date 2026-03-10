import os
from pathlib import Path
from config import UPLOAD_DIR


def get_file_path(relative_path: str) -> str:
    full_path = os.path.join(UPLOAD_DIR, relative_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    return full_path


def get_upload_dir() -> Path:
    path = Path(UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path
