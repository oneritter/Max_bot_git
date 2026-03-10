from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User
from auth import get_current_admin

router = APIRouter(prefix="/users", tags=["users"])


class UserOut(BaseModel):
    id: int
    max_user_id: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    status: Optional[str] = None
    full_name: Optional[str] = None


@router.get("", response_model=list[UserOut])
def list_users(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    q = db.query(User)
    if status:
        q = q.filter(User.status == status)
    if search:
        q = q.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.phone.ilike(f"%{search}%")) |
            (User.username.ilike(f"%{search}%"))
        )
    users = q.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for u in users:
        result.append(UserOut(
            id=u.id,
            max_user_id=u.max_user_id,
            username=u.username,
            full_name=u.full_name,
            phone=u.phone,
            status=u.status,
            created_at=u.created_at.isoformat() if u.created_at else None,
        ))
    return result


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=user.id,
        max_user_id=user.max_user_id,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        status=user.status,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.patch("/{user_id}", response_model=UserOut)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.status and body.status in ("pending", "approved", "blocked"):
        user.status = body.status
    if body.full_name is not None:
        user.full_name = body.full_name
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        max_user_id=user.max_user_id,
        username=user.username,
        full_name=user.full_name,
        phone=user.phone,
        status=user.status,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )
