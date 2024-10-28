#!/usr/bin/env python3

"""
this is the tasks model for our platform
"""
import pytz
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship, Session
import logging
from user import Base

logging.basicConfig(level=logging.Error, format='%(asctime)s - %(levelname)s - %(message)s')

EAT = pytz.timezone('Africa/Nairobi')

class TaskStatusEnum(str, Enum):
    """
    class definition to clarify the status of a task
    """
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELED = 'canceled'
class TaskPriorityEnum(str, Enum):
    """
    class definition to clarify the status of a task
    """
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'

class Task(Base):
    __tablename__ = 'tasks'    

    id = Column(Integer, primary_key=True)
    title = Column(string(100), nullable=False)
    description = Column(string(500))
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_tasker_id = Column(Integer, ForeignKey('users.id'))
    status = Column(Enum(TaskStatusEnum), defauly=TaskStatusEnum.PENDING)
    due_date = Column(DateTime)
    creation_date = Column(DateTime, default=lambda: datetime.now(EAT))
    completion_date = Column(DateTime, default=lambda: datetime.now(EAT))
    location_id = Column(Integer, ForeignKey('locations.id'))
    payment_amount = Column(Float)
    priority = Column(Enum(TaskPriorityEnum), default=TaskPriorityEnum.MEDIUM)
    creator = relationship("User", foreign_keys=[creator_id])
    assigned_tasker = relationship("User", foreign_keys=[assigned_tasker_id])
    location = relationship("Location")
    attachments = relationship("Attachment", backref="task")

    def __init__(self, title, description, creator_id, location_id, payment_amount, due_date=None, priority=TaskPriorityEnum.MEDIUM):
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.location_id = location_id
        self.payment_amount = payment_amount
        self.due_date = due_date
        self.priority = priority

    def create_task(self, session: Session):
        """
        method definition that allows creation of a task
        """
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            logging.error(f"Error creating task: {e}")
            session.rollback()

    def assign_tasker(self, session: Session, tasker_id: int):
        """
        method definition that allows a tasker to have a task
        """
        try:
            self.assigned_tasker_id = tasker_id
            session.commit()
            self.notify_user("Tasker assigned")
        except Exception as e:
            logging.error(f"Error assigning tasker: {e}")
            session.rollback()

    def change_status(self, session: Session, new_status: TaskStatusEnum):
        """
        method definition to change a task's status
        """
        try:
            self.status = new_status
            session.commit()
            self.notify_user(f"Task status changed to {new_status}")
        except Exception as e:
            logging.error(f"Error changing task status: {e}")
            session.rollback()

    def set_priority(self, session: Session, priority: TaskPriorityEnum):
        """
        method definition to set a task's priority
        """
        try:
            self.priority = priority
            session.commit()
        except Exception as e:
            logging.error(f"Error setting task priority: {e}")
            session.rollback()

    def add_attachment(self, session: Session, attachment):
        """
        method definition to add attachment to a task
        to give it more context
        """
        try:
            self.attachments.append(attachment)
            session.commit()
        except Exception as e:
            logging.error(f"Error adding attachment to task: {e}")
            session.rollback()

    def notify_user(self, message):
        """
        method definition to send notifications
        to a user regarding the task
        """
        try:
            notification = Notification(user_id=self.creator_id, content=message, task_id=self.id)
            session.add(notification)
            session.commit()
        except Exception as e:
            logging.error(f"Error sending notification: {e}")
            session.rollback()

    def audit_task_changes(self, session: Session, attribute, old_value, new_value):
        """
        method definition to audit changes made to a task
        """
        try:
            audit_log = AuditLog(
                    task_id=self.id,
                    attribute=attribute,
                    old_value=old_value,
                    new_value=new_value,
                    change_date=datetime.now(EAT)
                    )
            session.add(audit_log)
            session.commit()
        except Exception as e:
            logging.error(f"Error logging task audit: {e}")
            session.rollback()

    def cancel_task(self, session: Session):
        """
        method definition that allows a user to cancel a task
        """
        try:
            self.status = TaskStatusEnum.CANCELED
            session.commit()
            self.notify_user("Task successfully canceled.")
        except Exception as e:
            logging.error(f"Error canceling task: {e}")
            session.rollback()

    def get_duration(self):
        """
        method definition that calculates
        how long it took for the task to be completed
        """
        if self.creation_date and self.completion_date:
            return (self.completion_date - self.creation_date).total_seconds()
        else:
            logging.error("Unable to calculate task duration: Incomplete dates")
            return None

    def add_task_review(self, session: Session, review):
        """
        method definition that allows users
        to leave a review of a task
        """
        try:
            self.reviews.append(review)
            session.commit()
        except Exception as e:
            logging.error(f"Error adding task review: {e}")
            session.rollback()

    def add_milestone(self, session: Session, milestone):
        """
        method definition that allows users
        to add milestones for lengthy tasks
        """
        try:
            self.milestones.append(milestone)
            session.commit()
        except Exception as e:
            logging.error(f"Error adding task milestone: {e}")
            session.rollback()
