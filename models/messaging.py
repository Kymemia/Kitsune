#!/usr/bin/env python3
"""
this is the messaging model for our platform
it will allow the tasker and poster
to communicate with each other after a task has been claimed
"""
import pytz
import logging
from datetime import datetime
from sqlalchemy import (
        Column,
        Integer,
        String,
        ForeignKey,
        Enum,
        Text,
        DateTime
        )
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
EAT = pytz('Africa/Nairobi')


class MessageStatus(Enum):
    SENT = 'sent'
    DELIVERED = 'delivered'
    READ = 'read'

class MessageThread(Base):
    __tablename__ = 'message_threads'

    thread_id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    created_at = Column(DateTime, default=datetime.now(EAT))
    messages = relationship("Messages", back_populates="thread")

class Message(Base):
    __tablename__ = 'messages'

    message_id = Column(Ineger, primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'), nullable=False)
    thread_id = Column(Integer, ForeignKey('message_threads.thread_id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    message_content = Column(Text, nullable=False)
    attachments = Column(String)
    timestamp = Column(DateTime, default=datetime.now(EAT))
    status = Column(Enum(MessageStatus), default=MessageStatus.SENT)
    thread = relationship("MessageThread", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[sender_id])

    def send_message(self, receiver_id, content, attachments=None):
        """
        method definition that allows users to send messages
        """
        if not receiver_id or not content:
            raise ValueError("Receiver ID and content cannot be empty.")

        self.receiver_id = receiver_id
        self.message_content = content
        if attachments:
            self.attachments = attachments
        self.status = MessageStatus.SENT
        self.timeseamp = datetime.now(EAT)

        if not self.thread_id:
            self.thread = MessageThread.create_message_thread(self.task_id)

        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        self.notify_users()
        return self

    def receive_message(self, mark_as_read=False):
        """
        method definition that allows users to receive messages
        """
        self.status = MessageStatus.DELIVERED

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        if mark_as_read:
            self.mark_as_read()

        logging.info(f"Message {self.message_id} delivered to user {self.receiver_id}")

        self.notify_users()
        return self

    def attach_file(self, file_link):
        """
        method definition that allows users
        to add attachments to their files
        """
        if not file_link:
            raise ValueError("Invalid file link")

        if isinstance(self.attachments, str):
            self.attachments = self.attachments.split(',')
        elif not isinstance(self.attachments, list):
            self.attachments = []

        if file_link not in self.attachments:
            self.attachments.append(file_link)

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

        logging.info(f"File {file_link} attached to message { self.message_id}")
        return self.attachments

    @classmethod
    def fetch_messages(cls, thread_id):
        """
        method definition that allows users to fetch all their messages
        """
        return cls.query.filter_by(thread_id=thread.id).all()

    def notify_users(self):
        """
        method definition to notify users of incoming messages
        """
        sender_notification = Notification(
                user_id=self.sender_id,
                notification_type='message_sent',
                content=f"Message sent to {self.receiver_id}: {self.content}"
                )
        sender_notification.send()

        receiver_notification = Notification(
                user_id=self.receiver_id,
                notification_type='new_message',
                content=f"Message received from {self.sender_id}: {self.content}"
                )

        logging.info(f"Notifications sent for message: {self.message_id} from {self.sender_id} to {self.receiver_id}")

    @classmethod
    def create_message_thread(cls, task_id):
        """
        method definition that creates a message thread
        for a specific task
        """
        task = session.query(Task).filter_by(task_id=task_id).first()
        if not task:
            raise ValueError(f"Task with ID {task_id} does not exist")
        new_thread = MessageThread(task_id=task_id)
        session.add(new_thread)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(F"Error creating message thread for task {task_id}: {e}")
            raise

        logging.info(f"Thread created with ID {new_thread.thread_id} for task {task_id}")
        return new_thread
