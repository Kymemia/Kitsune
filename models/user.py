#!/usr/bin/env python3

"""
this is the user model for Kitsune
"""
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy import Date, Enum, DateTime, String, UniqueConstraint
from datetime import datetime
import enum
import bcrypt # Necessary for hashing

Base = declarative_base()


class User(Base):
    """
    this will be the class definition for our user model
    """
    __tablename__ = "users"

    uid = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(256), unique=True, nullable=False)
    user_type = Column(Enum("user", "tasker", "admin", name="user_type_enum"), default="user", nullable=False)
    firstname = Column(String(256))
    lastname = Column(String(256))
    age = Column(Integer)
    email = Column(String, nullable=False)
    phone_number = Column(String(256))
    hashed_password = Column(String(256))
    account_creation_date = Column(DateTime, default=datetime.utcnow)
    last_login_date = Column(DateTime)
    user_type = Column(Enum(UserType), default=UserType.user)
    credit_card = Column(String(60))

    """
    methods to be implemented
    __init__: to specify needed attr  
    reset_password
    check password
    to_dict
    __str__
    __repr__
    """

    def __init__(self, username, email, hashed_password, **kwargs):
        """
        method definition to initialize the necessary fields
        """
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.firstname = kwargs.get('firstname')
        self.lastname = kwargs.get('lastname')
        self.age = kwargs.get('age')
        self.phone_number = kwargs.get('user_type', 'user')
        self.user_type = kwargs.get('user_type', 'user')
        self.last_login_date = kwargs.get('last_login_date')
        self.credit_card = kwargs.get('credit_card')
        self.account_creation_date = kwargs.get('account_creation_date', datetime.utcnow())


    def set_password(self, password):
        """
        method definition to hash the password & store it using bcrypt.
        """
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """
        method definition to check if the password provided
        by the user matches the stored hashed password.
        """
        return bcrypt.checkpw(password.encode('utf-8'). self.hashed_password.encode('utf-8'))

    def reset_password(self, password):
        """
        method definition to reset the user's password
        """
        self.self_password(new_password)
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

    def to_dict(self):
        """
        method definition to display all the meaningful attributes
        """
