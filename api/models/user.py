"""
User model for MediAI authentication and RBAC.

Stores user credentials, profile information, and role assignments.
"""

from datetime import datetime
from typing import Optional

from core.database import Base
from core.rbac import Role
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship


class User(Base):
    """User model for authentication and authorization"""

    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)

    # Role-based access control
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)

    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Profile
    avatar_url = Column(String(500), nullable=True)
    specialty = Column(String(100), nullable=True)  # For doctors
    department = Column(String(100), nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
