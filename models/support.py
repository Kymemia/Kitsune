#!/usr/bin/env python3

"""
This is the support model for our platform
"""
import pytz
from sqlalchemy import Column, Integer, String, Enum, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

EAT = pytz.timezone('Africa/Nairobi')

class TicketStatus(PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class PriorityLevel(PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Category(PyEnum):
    TECHNICAL = "technical issue"
    ACCOUNT = "account query"
    PAYMENT = "payment issue"

class SupportTicket(Base):
    __tablename__ = 'support_tickets'

    ticket_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    support_agent_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    ticket_status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    priority_level = Column(Enum(PriorityLevel), nullable=False)
    category = Column(Enum(Category), nullable=False)
    subject = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    attachments = Column(Text, nullable=False)
    created_date = Column(DateTime, default=datetime.now(EAT), nullable=False)
    updated_date = Column(DateTime, onupdate=datetime.now(EAT))
    resolution_date = Column(DateTime, nullable=True)
    resolution_details = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User", foreign_keys=[user_id])
    support_agent = relationship("User", foreign_keys=[support_agent_id])

    def create_ticket(
            self, user_id: int,
            subject: str, description: str,
            category: Category,
            priority_level: PriorityLevel
            ):
        """
        method definition to create a support ticket
        """
        self.user_id = user_id
        self.subject = subject
        self.description = description
        self.category = category
        self.priority_level = priority_level
        self.created_date = datetime.now(EAT)
        self.ticket_status = TicketStatus.OPEN

    def assign_ticket(self, support_agent_id: int):
        """
        method definition to assign the ticket to an agent
        """
        self.support_agent_id = support_agent_id
        self.ticket_status = TicketStatus.IN_PROGRESS
        self.update_date = datetime.now(EAT)

    def update_ticket_status(self, new_status: TicketStatus):
        """
        method definition to update the ticket's status
        """
        self.ticket_status = new_status
        self.updated_date = datetime.now(EAT)

    def add_note(self, note: str):
        """
        method definition that allows
        the support agent to add an internal note for the ticket
        """
        self.notes = (self.notes or "") + f"\n{datetime.now(EAT)}: {note}"

    def submit_resolution(self, resolution_details: str):
        """
        method definition to submit
        the resolution details for the ticket
        """
        self.resolution_details = resolution_details
        self.ticket_status = TicketStatus.RESOLVED
        self.resolution_date = datetime.now(EAT)

    def close_ticket(self):
        """
        method definition to close a ticket after resolution
        """
        self.ticket_status = TicketStatus.CLOSED
        self.updated_dare = datetime.now(EAT)

    def submit_feedback(self, feedback: str):
        """
        method definition that allows a user
        to submit feedback about the support given
        """
        self.feedback = feedback

    def attach_file(self, attachment: str):
        """
        method definition to attach a file to the ticket
        """
        self.attachments = (self.attachments or "") + f"\n{attachment}"

    def notify_user_and_agent(self, message: str):
        """
        method definition to notify the user
        & agent about updates to the ticket
        """
        notification_user = Notification(
                user_id=self.user_id,
                message=f"Ticket #{self.ticket_id}: {message}",
                created_at=datetime.now(EAT)
                )
        notification_agent = None
        if self.support_agent_id:
            notification_agent = Notification(
                    user_id=self.support_agent_id,
                    message=f"Ticket #{self.ticket_id}: {message}",
                    created_at=datetime.now(EAT)
                    )

        session.add(notification_user)
        if notification_agent:
            session.add(notification_agent)
        session.commit()

    def audit_support_tickets(self):
        """
        method definition to log changes for auditing purposes
        """
        audity_entry = SupportTicketAudit(
                ticket_id=self.ticket_id,
                status=self.ticket_status.value,
                updated_at=datetime.now(EAT),
                notes=self.notes
                )
        session.add(audit_entry)
        session.commit()

    def fetch_ticket_history(self):
        """
        method definition to retrieve the history
        of changes made to a certain ticket
        """
        return session.query(SupportTicketAudit).filter_by(ticket_id=self.ticket_id).order_by(SupportTicketAudit.updated_at.asc()).all()
