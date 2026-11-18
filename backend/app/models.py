from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(120), nullable=False)
    email = Column(String(190), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="farmer")
    preferred_language = Column(String(5), nullable=False, default="en")
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    cases = relationship("CropCase", back_populates="farmer")

class CropCase(Base):
    __tablename__ = "crop_cases"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    crop_name = Column(String(80), nullable=False)
    location = Column(String(120), nullable=True)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=False)
    status = Column(String(30), nullable=False, default="submitted")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    farmer = relationship("User", back_populates="cases")
    reviews = relationship("ExpertReview", back_populates="case", cascade="all, delete-orphan")

class ExpertReview(Base):
    __tablename__ = "expert_reviews"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("crop_cases.id"), nullable=False, index=True)
    expert_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assessment = Column(Text, nullable=False)
    recommended_next_steps = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    case = relationship("CropCase", back_populates="reviews")
