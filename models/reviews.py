#!/usr/bin/env python3

"""
this is the reviews model for our platform
"""
import logging
import pytz
from storage import Storage
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum

class Review:
    storage = Storage()

    review_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.now(pytz.timezone('Africa/Nairobi')))
    status = Column(Enum("approved", "pending", "rejected"), default="pending")

    def __init__(self, user_id, task_id, rating, comment):
        self.user_id = user_id
        self.task_id = task_id
        self.rating = rating
        self.comment = comment

    @classmethod
    def create_review(cls, user_id, task_id, rating, comment):
        storage = Storage()
        try:
            review = cls(user_id=user_id, task_id=task_id, rating=rating, comment=comment)
            storage.db.session.add(review)
            storage.db.session.commit()
            return review
        except Exception as e:
            logging.error(f"Error creating review: {e}")
            storage.db.session.rollback()
            return None

    @classmethod
    def update_review(cls, review_id, rating=None, comment=None, status=None):
        storage = Storage()
        try:
            review = storage.db.session.query(cls).get(review_id)
            if review:
                if rating is not None:
                    review.rating = rating
                if comment is not None:
                    review.comment = comment
                if status is not None:
                    review.status = status
                storage.db.session.commit()
                return review
            else:
                logging.warning(f"Review with ID {review_id} not found.")
                return None
        except Exception as e:
            logging.error(f"Error updating review: {e}")
            storage.db.session.rollback()
            return None

    @classmethod
    def fetch_reviews(cls, user_id=None, task_id=None):
        storage = Storage()
        try:
            query = storage.db.session.query(cls)
            if user_id:
                query = query.filter_by(user_id=user_id)
            if task_id:
                query = query.filter_by(task_id=task_id)
            return query.all()
        except Exception as e:
            logging.error(f"Error fetching reviews: {e}")
            return None

    @classmethod
    def delete_review(cls, review_id):
        storage = Storage()
        try:
            review = storage.db.session.query(cls).get(review_id)
            if review:
                storage.db.session.delete(review)
                storage.db.session.commit()
                return True
            else:
                logging.warning(f"Review with ID {review_id} not found.")
                return False
        except Exception as e:
            logging.error(f"Error deleting review: {e}")
            storage.db.session.rollback()
            return False

    @classmethod
    def approve_review(cls, review_id):
        storage = Storage()
        try:
            review = storage.db.session.query(cls).get(review_id)
            if review:
                review.status = "approved"
                storage.db.session.commit()
                return review
            else:
                logging.warning(f"Review with ID {review_id} not found.")
                return None
        except Exception as e:
            logging.error(f"Error approving review: {e}")
            storage.db.session.rollback()
            return None
