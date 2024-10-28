#!/usr/bin/env python3

"""
this is the attachment model for our platform
"""
import os
import logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from user import Base

logging.basicConfig(level=logging.ERROR, format'%(asctime)s - %(levelname)s - %(message)s')

class Attachment(Base):
    """
    class definition for the attachment model
    """
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(100), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploader_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)

    uploader = relationship("User")
    task = relationship("Task", back_populates="attachments")
    message = relationship("Message", back_populates="attachments")

    def __init__(self, filename, file_path, file_type, uploader_id, task_id=None, message_id=None):
        self.filename = filename
        self.file_path = file_path
        self.file_type = file_type
        self.uploader_id = uploader_id
        self.task_id = task_id
        self.message_id = message_id

    def save_to_database(self, session):
        """
        method definition to save
        the attachment to the database
        """
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logging.error(f"Error saving attachment to database: {e}")
            session.rollback()

    def delete_attachment(self, session):
        """
        method definition to delete the attachment
        both from the database and filesystem
        """
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            else:
                logging.error(f"File not found on path: {self.file_path}")

            session.delete(self)
            session.commit()
        except Exception as e:
            logging.error(f"Error deleting attachment: {e}")
            session.rollback()

    def get_file_info(self):
        """
        method definition to retrieve metadata information
        about the attachment
        """
        return {
            "filename": self.filename,
            "file_type": self.file_type,
            "upload_date": self.upload_date,
            "uploader_id": self.uploader_id,
            "file_path": self.file_path
        }
