from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Category
from auth import get_current_admin

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    sort_order: int = 0
    icon: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class CategoryTree(CategoryOut):
    children: list["CategoryTree"] = []


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    sort_order: int = 0
    icon: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None


def _build_tree(categories: list[Category], parent_id: int | None = None) -> list[dict]:
    tree = []
    for cat in categories:
        if cat.parent_id == parent_id:
            node = {
                "id": cat.id,
                "name": cat.name,
                "slug": cat.slug,
                "parent_id": cat.parent_id,
                "sort_order": cat.sort_order,
                "icon": cat.icon,
                "is_active": cat.is_active,
                "children": _build_tree(categories, cat.id),
            }
            tree.append(node)
    tree.sort(key=lambda x: x["sort_order"])
    return tree


@router.get("", response_model=list[CategoryTree])
def list_categories(db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    all_cats = db.query(Category).all()
    return _build_tree(all_cats, parent_id=None)


@router.get("/flat", response_model=list[CategoryOut])
def list_categories_flat(db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    return db.query(Category).order_by(Category.sort_order).all()


@router.post("", response_model=CategoryOut)
def create_category(body: CategoryCreate, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    existing = db.query(Category).filter(Category.slug == body.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    cat = Category(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.patch("/{cat_id}", response_model=CategoryOut)
def update_category(cat_id: int, body: CategoryUpdate, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    children = db.query(Category).filter(Category.parent_id == cat_id).count()
    if children > 0:
        raise HTTPException(status_code=400, detail="Cannot delete category with children. Remove children first.")
    db.delete(cat)
    db.commit()
    return {"ok": True}
