#!/usr/bin/env python3

"""
this is the user model for Kitsune
"""
import pytz
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy import Date, Enum, DateTime, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, Union

Base = declarative_base()
EAT = pytz.timezone('Africa/Nairobi')


class User(Base):
    """
    this will be the class definition for our user model
    """
    __tablename__ = "users"

    uid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, nullable=False)
    username = Column(String(256), unique=True, nullable=False)
    user_type = Column(Enum("user", "tasker", "admin", name="user_type_enum"), default="user", nullable=False)
    firstname = Column(String(256))
    lastname = Column(String(256))
    age = Column(Integer)
    email = Column(String, nullable=False)
    phone_number = Column(String(256))
    hashed_password = Column(String(256), nullable=False)
    account_creation_date = Column(DateTime, default=lambda: datetime.now(EAT))
    last_login_date = Column(DateTime)
    credit_card = Column(String(60))

    def __init__(self, username: str,
            email: str, hashed_password: str,
            firstname: Optional[str] = None,
            lastname: Optional[str] = None,
            age: Optional[int] = None,
            phone_number: Optional[str] = None,
            user_type: str = 'user',
            last_login_date: Optional[str] = None,
            credit_card: Optional[str] = None,
            account_creation_date: datetime = datetime.utcnow(),
            **kwargs
            ):
        """
        method definition to initialize the necessary fields
        """
        self.uid = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.hashed_password = set_password(hashed_password)
        self.firstname = firstname
        self.lastname = lastname
        self.age = age
        self.phone_number = phone_number
        self.user_type = user_type
        self.last_login_date = last_login_date
        self.credit_card = credit_card
        self.account_creation_date = account_creation_date


    def set_password(self, password: str):
        """
        method definition to hash the password & store it using bcrypt.
        """
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        method definition to check if the password provided
        by the user matches the stored hashed password.
        """
        return check_password_hash(self.hashed_password, password)

    def reset_password(self, password: str):
        """
        method definition to reset the user's password
        """
        self.hashed_password = generate_password_hash(new_password)

    def __repr__(self):
        """
        method definition to display key attributes
        """
        return f"<User(username='{self.username}', email='{self.email}', user_type='{self.user_type}')>"

    def __str__(self):
        """
        method definition to display values important to the end-user
        """
        return f"User: {self.firstname} {self.lastname} ({self.username})"

    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        method definition to display all the meaningful attributes
        """
        user_dict = {
                "uid": self.uid, "username": self.username,
                "user_type": self.user_type, "firstname": self.firstname,
                "lastname": self.lastname, "age": self.age,
                "email": self.email, "phone_number": self.phone_number,
                "account_creation_date": self.account_creation_date.isoformat() if self.account_creation_date else None,
                "last_login_date": self.last_login_date.isoformat() if self.last_login_date else None,
                }

        if include_sensitive:
            user_dict["credit_card"] = self.credit_card
            user_dict["hashed_password"] = self.hashed_password

        return user_dict
