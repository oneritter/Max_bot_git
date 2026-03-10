import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Document
from auth import get_current_admin
from config import UPLOAD_DIR

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentOut(BaseModel):
    id: int
    title: str
    file_path: str
    file_type: Optional[str] = None
    category_id: Optional[int] = None
    sort_order: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


@router.get("", response_model=list[DocumentOut])
def list_documents(
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    q = db.query(Document)
    if category_id is not None:
        q = q.filter(Document.category_id == category_id)
    return q.order_by(Document.sort_order).all()


@router.post("", response_model=DocumentOut)
def upload_document(
    title: str = Form(...),
    category_id: int = Form(None),
    sort_order: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Determine file type
    ext = os.path.splitext(file.filename or "")[1].lower().lstrip(".")
    safe_name = file.filename.replace(" ", "_") if file.filename else "file"

    # Avoid overwriting
    dest_path = os.path.join(UPLOAD_DIR, safe_name)
    counter = 1
    base, extension = os.path.splitext(dest_path)
    while os.path.exists(dest_path):
        dest_path = f"{base}_{counter}{extension}"
        counter += 1

    with open(dest_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    relative_path = os.path.basename(dest_path)

    doc = Document(
        title=title,
        file_path=relative_path,
        file_type=ext,
        category_id=category_id,
        sort_order=sort_order,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.patch("/{doc_id}", response_model=DocumentOut)
def update_document(
    doc_id: int,
    body: DocumentUpdate,
    db: Session = Depends(get_db),
    _admin: dict = Depends(get_current_admin),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if body.title is not None:
        doc.title = body.title
    if body.category_id is not None:
        doc.category_id = body.category_id
    if body.sort_order is not None:
        doc.sort_order = body.sort_order
    if body.is_active is not None:
        doc.is_active = body.is_active
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    # Remove file
    full_path = os.path.join(UPLOAD_DIR, doc.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    db.delete(doc)
    db.commit()
    return {"ok": True}
