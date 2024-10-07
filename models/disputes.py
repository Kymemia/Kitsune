#!/usr/bin/env python3

"""
this is the disputes model for our platform
"""
import pytz
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLAlchemy, Text, DateTime
from sqlalchemy.orm import relationship
from user import Base
from flask import current_app

EAT = pytz.timezone('Africa/Nairobi')

class DisputeStatus(Enum):
    OPEN = "open"
    UNDER_REVIEW = "under review"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class DisputeReason(Enum):
    TASK_NOT_COMPLETED = "task not completed"
    PAYMENT_ISSUES = "payment issues"
    QUALITY_OF_WORK = "quality of work"


class Dispute(Base):
    __tablename__ = 'disputes'

    dispute_id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'), nullable=False)
    poster_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    tasker_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(SQLAlchemyEnum(DisputeStatus), default=DisputeStatus.OPEN)
    reason = Column(SQLAlchemyEnum(DisputeReason), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(Text)
    resolution_outcome = Column(SQLAlchemyEnum(DisputeStatus))
    resolution_date = Column(DateTime)
    admin_id = Column(Integer, ForeignKey('admins.admin_id'))
    created_date = Column(DateTime, default=datetime.now(EAT))
    update_date = Column(DateTime, onupdate=datetime.now(EAT))

    task = relationship('Task', backref='disputes')
    poster = relationship('User', foreign_keys=[poster_id])
    tasker = relationship('USer', foreign_keys=[tasker_id])
    admin = relationship('Admin', backref='disputes_handled')

    def create_dispute(self, task_id, poster_id, tasker_id, reason, description):
        """
        method definition to file a new dispute
        """
        self.task_id = task_id
        self.poster_id = poster_id
        self.tasker_id = tasker_id
        self.reason = reason
        self.description = description
        db.session.add(self)
        db.session.commit()

    def submit_evidence(self, evidence):
        """
        method definition to allow users
        to submit evidence related to a dispute
        """
        self.evidence = evidence
        db.session.commit()

    def update_status(self, new_status):
        """
        method definition to update status of the claim
        """
        self.status = new_status
        self.audit_changes()
        db.session.commit()

    def resolve_dispute(self, outcome):
        """
        method definition to resolve the dispute
        and set the resolution outcome
        """
        self.resolution_outcome = outcome
        self.resolution_date = datetime.now(EAT)
        self.status = DisputeStatus.RESOLVED
        self.audit_changes()
        self.notify_users()
        db.session.commit()

    def escalate_dispute(self):
        """
        method definition to allow one to escalate
        the dispute, should the need arise
        """
        self.status = DisputeStatus.ESCALATED
        self.audit_changes()
        self.notify_users()
        db.session.commit()

    def notify_users(self):
        """
        this method sends notifications to involved parties
        regarding the status of the dispute
        """
        poster_email = self.poster.email
        tasker_email = self.tasker.email
        message = f"Dispute {self.dispute_id} status updated to {self.status.value}."
        
        with current_app.app_context():
            current_app.mail.send_message(
                    subject="Dispute Status Update",
                    recipients=[poster_email, tasker_email],
                    body=message
                    )

    def audit_changes(self):
        """
        this method logs every change in dispute status
        """
        log_entry = f"Dispute {self.dispute_id} status changed to {self.status.value} on {datetime.now(EAT)}"
        print(log_entry)

    @staticmethod
    def fetch_dispute_history(dispute_id):
        """
        this method retrieves the history of changes & updates
        for a specific dispute
        """
        dispute = Dispute.query.filter_by(dispute_id=dispute_id).first()
        if dispute:
            return {
                    "dispute_id": dispute.dispute_id,
                    "status": dispute.status.value,
                    "reason": dispute.reason.value,
                    "description": dispute.description,
                    "created_date": dispute.created_date,
                    "updated_date": dispute.updated_date,
                    "resolution_outcome": dispute.resolution_outcome.value if dispute.resolution_outcome else None
                    "resolution_date": dispute.resolution_date,
                    "evidence": dispute.evidence
                    }
        return None
