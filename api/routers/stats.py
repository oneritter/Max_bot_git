from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, Document, Category, TrainingRequest, FeedbackQuestion
from auth import get_current_admin

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
def get_stats(db: Session = Depends(get_db), _admin: dict = Depends(get_current_admin)):
    total_users = db.query(User).count()
    pending_users = db.query(User).filter(User.status == "pending").count()
    approved_users = db.query(User).filter(User.status == "approved").count()
    blocked_users = db.query(User).filter(User.status == "blocked").count()
    total_documents = db.query(Document).count()
    total_categories = db.query(Category).count()
    total_training = db.query(TrainingRequest).count()
    total_feedback = db.query(FeedbackQuestion).count()
    unresolved_feedback = db.query(FeedbackQuestion).filter(FeedbackQuestion.is_resolved.is_(False)).count()

    return {
        "users": {
            "total": total_users,
            "pending": pending_users,
            "approved": approved_users,
            "blocked": blocked_users,
        },
        "documents": total_documents,
        "categories": total_categories,
        "training_requests": total_training,
        "feedback": {
            "total": total_feedback,
            "unresolved": unresolved_feedback,
        },
    }
