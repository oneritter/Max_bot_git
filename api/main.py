from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db, SessionLocal
from models import AdminUser
from auth import hash_password
from config import ADMIN_USERNAME, ADMIN_PASSWORD
from routers import auth_router, users, documents, categories, stats

app = FastAPI(title="Finbox Bot Admin API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(AdminUser).filter(AdminUser.username == ADMIN_USERNAME).first()
        if not existing:
            admin = AdminUser(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD))
            db.add(admin)
            db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
