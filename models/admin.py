#!/usr/bin/env python3

"""
admin model
"""
import pytz
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from user import Base

EAT = pytz.timezone('Africa/Nairobi')

class Admin(Base):
    __tablename__ = 'admins'

    admin_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_date = Column(DateTime, default=datetime.now(EAT))
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Admin {self.username}"

    def set_password(self, password: str) -> None:
        """
        method definition to hash & store the password
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        method definition to check whether
        the provided password matches the hashed password
        """
        return check_password_hash(self.password_hash, password)
