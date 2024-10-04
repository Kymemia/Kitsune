#!/usr/bin/python3

"""
this is the code for the payements model
it will be handling payment data,
handling escrow, tracking transactions, & payment details
"""
import pytz
from user import Base
from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey, Boolean
from datetime import datetime

EAT = pytz.timezone('Africa/Nairobi')


class Payment(Base):
    """
    class definition that'll have
    all the vital aspects of the payment model
    """
    __tablename__ = "payments"

    id = Column(String, primary_key=True)
    task_id = Column(String, ForeignKey('tasks.id'), nullable=False)
    poster_id = Column(String, ForeignKey('users.id'), nullable=False)
    tasker_id = Column(String, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    transaction_status = Column(Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    date_of_payment = Column(DateTime, default=datetime.now(EAT))
    escrow_status = Column(Boolean, default=True)
    refund_status = Column(Boolean, default=False)
    mpesa_transaction_ref = Column(String, nullable=True)
    visa_transaction_ref = Column(String, nullable=True)

    def update_status(self, new_status):
        """
        method definition to update the status of the payment
        """
        self.transaction_status = new_status
        self.date_of_payment = datetime.now(EAT)
        self.save_to_db()

    def release_escrow(self):
        """
        method definition to release escrow payment
        """
        self.escrow_status = False
        self.disbursement_date = datetime.now(EAT)
        self.save_to_db()

    def save_to_db(self):
        """
        method definition to ensure proper updating
        of transactions to the database
        """
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
