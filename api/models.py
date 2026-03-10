from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    max_user_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    training_requests = relationship("TrainingRequest", back_populates="user")
    feedback_questions = relationship("FeedbackQuestion", back_populates="user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    parent = relationship("Category", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="category")
    external_links = relationship("ExternalLink", back_populates="category")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    max_file_id = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="documents")


class ExternalLink(Base):
    __tablename__ = "external_links"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sort_order = Column(Integer, default=0)

    category = relationship("Category", back_populates="external_links")


class TrainingRequest(Base):
    __tablename__ = "training_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    partner_name = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    date = Column(String, nullable=True)
    time = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_to_sheets = Column(Boolean, default=False)

    user = relationship("User", back_populates="training_requests")


class FeedbackQuestion(Base):
    __tablename__ = "feedback_questions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

    user = relationship("User", back_populates="feedback_questions")


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
