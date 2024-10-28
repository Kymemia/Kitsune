#!/usr/bin/env python3
"""
this is the audit logs model for our platform
"""
import logging
import pytz
import csv
import json
from datetime import datetime
from storage import Storage
from sqlalchemy import Enum, String, JSON
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

ACTION_TYPES = Enum('create', 'update', 'delete', 'view')
ENTITY_TYPES = Enum('user', 'task', 'payment')


class AuditLog:
    """
    class definition for the audit logs model
    """
    def __init__(self, user_id, action_type,
            entity_type, entity_id,
            details=None, ip_address=None,
            status='success'):
        self.log_id = None
        self.user_id = user_id
        self.action_type = action_type
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.timestamp = datetime.now(pytz.timezone('Africa/Nairobi'))
        self.details = details
        self.ip_address = ip_address
        self.status = status

    def log_action(self):
        """
        method definition that records an action in the audit log
        """
        try:
            storage = Storage()
            log_entry = {
                    'user_id': self.user_id,
                    'action_type': self.action_type,
                    'entity_type': self.entity_type,
                    'timestamp': self.timestamp,
                    'details': self.details,
                    'ip_address': self.ip_address,
                    'status': self.status
                    }
            storage.insert(log_entry)
        except SQLAlchemyError as e:
            logger.error(f"Failed to log action: {e}")
            raise

    @staticmethod
    def fetch_logs(user_id=None, entity_type=None, date_range=None):
        """
        method definition to retrieve logs based on some filters
        """
        try:
            storage = Storage()
            query = storage.query(AuditLog)

            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            if date_range:
                start_date, end_date = date_range
                query = query.filter(AuditLog.timestamp.between(start_date, end_date))

            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching logs: {e}")
            raise

    @staticmethod
    def search_logs(keyword):
        """
        method definition that allows one to search logs based
        on a keyword in the 'details' field
        """
        try:
            storage = Storage()
            return storage.query(AuditLog).filter(
                    AuditLog.details.contains(keyword)
                    ).all()
        except SQLAlchemyError as e:
            logger.error(f"Error searching logs with keyword '{keyword}': {e}")
            raise

    @staticmethod
    def filter_logs(status=None, action_type=None):
        """
        method definition that filters logs based
        on status or action type
        """
        try:
            storage = Storage()
            query = storage.query(AuditLog)

            if status:
                query = query.filter(AuditLog.status == status)
            if action_type:
                query = query.filter(AuditLog.action_type == action_type)

            return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error filtering logs: {e}")
            raise

    @staticmethod
    def export_logs(file_format='csv'):
        """
        method definition that exports logs to a specified file format
        """
        logs = AuditLog.fetch_logs()
        try:
            if file_format == 'csv':
                file_name = "logs/exported_logs"
                with open(file_name, mode='w', newline='') as csvfile:
                    fieldnames = [
                        'log_id', 'user_id', 'action_type', 'entity_type',
                        'entity_id', 'timestamp', 'details', 'ip_address', 'status'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()
                    for log in logs:
                        writer.writerow({
                            'log_id': log.log_id,
                            'user_id': log.user_id,
                            'action_type': log.action_type,
                            'entity_type': log.entity_type,
                            'entity_id': log.entity_id,
                            'timestamp': log.timestamp.isoformat(),
                            'details': log.details,
                            'ip_address': log.ip_address,
                            'status': log.status
                        })
                logger.info(f"Logs exported successfully to {file_name}.")

            elif file_format == 'json':
                file_name = f"{file_path}.json"
                with open(file_name, mode='w') as jsonfile:
                    json_logs = [
                        {
                            'log_id': log.log_id,
                            'user_id': log.user_id,
                            'action_type': log.action_type,
                            'entity_type': log.entity_type,
                            'entity_id': log.entity_id,
                            'timestamp': log.timestamp.isoformat(),
                            'details': log.details,
                            'ip_address': log.ip_address,
                            'status': log.status
                        }
                        for log in logs
                    ]
                    json.dump(json_logs, jsonfile, indent=4)
                logger.info(f"Logs exported successfully to {file_name}.")

            else:
                logger.error("Unsupported file format for export.")
                raise ValueError("Unsupported file format for export.")
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            raise

    @staticmethod
    def generate_summary(time_period=None):
        """
        method definition that generates a summary of log actions
        for a certain time period
        """
        try:
            storage = Storage()
            query = storage.query(AuditLog).with_entities(
                    AuditLog.action_type,
                    db.func.count(AuditLog.action_type)
                    ).group_by(AuditLog.action_type)
            if time_period:
                start_date, end_date = time_period
                query = query.filter(AuditLog.timestamp.between(start_date, end_date))

            return query.all()
        except SQLAlchemyError as e:
            logging.error(f"Error generating summary: {e}")
            raise
