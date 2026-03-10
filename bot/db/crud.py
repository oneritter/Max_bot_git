from sqlalchemy.orm import Session
from db.models import User, Category, Document, ExternalLink, TrainingRequest, FeedbackQuestion


# === Users ===

def get_user_by_max_id(db: Session, max_user_id: str) -> User | None:
    return db.query(User).filter(User.max_user_id == str(max_user_id)).first()


def create_user(db: Session, max_user_id: str, username: str = None, full_name: str = None, phone: str = None, status: str = "pending") -> User:
    user = User(max_user_id=str(max_user_id), username=username, full_name=full_name, phone=phone, status=status)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_status(db: Session, user_id: int, status: str) -> User | None:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.status = status
        db.commit()
        db.refresh(user)
    return user


def update_user_fields(db: Session, user: User, **kwargs) -> User:
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


# === Categories ===

def get_root_categories(db: Session):
    return db.query(Category).filter(
        Category.parent_id.is_(None),
        Category.is_active.is_(True)
    ).order_by(Category.sort_order).all()


def get_children_categories(db: Session, parent_id: int):
    return db.query(Category).filter(
        Category.parent_id == parent_id,
        Category.is_active.is_(True)
    ).order_by(Category.sort_order).all()


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return db.query(Category).filter(Category.slug == slug, Category.is_active.is_(True)).first()


# === Documents ===

def get_documents_by_category(db: Session, category_id: int):
    return db.query(Document).filter(
        Document.category_id == category_id,
        Document.is_active.is_(True)
    ).order_by(Document.sort_order).all()


def update_document_file_id(db: Session, doc_id: int, max_file_id: str):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc:
        doc.max_file_id = max_file_id
        db.commit()


# === External Links ===

def get_links_by_category(db: Session, category_id: int):
    return db.query(ExternalLink).filter(
        ExternalLink.category_id == category_id
    ).order_by(ExternalLink.sort_order).all()


# === Training Requests ===

def create_training_request(db: Session, user_id: int, partner_name: str, surname: str, phone: str, topic: str, date: str, time: str) -> TrainingRequest:
    req = TrainingRequest(
        user_id=user_id, partner_name=partner_name, surname=surname,
        phone=phone, topic=topic, date=date, time=time
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


# === Feedback ===

def create_feedback(db: Session, user_id: int, question: str) -> FeedbackQuestion:
    fb = FeedbackQuestion(user_id=user_id, question=question)
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return fb
