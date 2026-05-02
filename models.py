from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Todo(Base):
    __tablename__ = "todo"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    text = Column(String)
    status = Column(String, default="to do")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    # 🔗 Relationship
    recommendations = relationship("Recommendation", back_populates="user")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    # 🔗 Foreign Key
    user_id = Column(Integer, ForeignKey("users.id"))

    crop = Column(String)
    lat = Column(String)
    lon = Column(String)
    result = Column(String)  # JSON string

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔗 Relationship
    user = relationship("User", back_populates="recommendations")