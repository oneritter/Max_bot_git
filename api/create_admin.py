"""CLI script to create an admin user."""
import sys
from getpass import getpass

from database import init_db, SessionLocal
from models import AdminUser
from auth import hash_password


def main():
    init_db()

    username = input("Admin username: ").strip()
    if not username:
        print("Username cannot be empty")
        sys.exit(1)

    password = getpass("Admin password: ")
    if len(password) < 4:
        print("Password must be at least 4 characters")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == username).first()
        if existing:
            print(f"Admin '{username}' already exists")
            sys.exit(1)

        admin = AdminUser(username=username, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        print(f"Admin '{username}' created successfully")
    finally:
        db.close()


if __name__ == "__main__":
    main()
