#!/usr/bin/env python3

"""
this be the analytics model for our platform
"""
import logging
import json
import csv
import pytz
from datetime import datetime
from sqlalchemy import JSON, String, Enum, Integer, Float
from sqlalchemy.exc import SQLAlchemyError
from storage import Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

storage = Storage()


class Analytics():
    """
    class definition for the analytics
    for different metrics in our platform
    """
    __tablename__ = 'analytics'

    analytics_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'), nullable=True)
    metric_type = Column(String(50), nullable=False)
    metric_value = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.now(pytz.timezone('Africa/Nairobi')))
    report_data = Column(JSON, nullable=True)

    def record_metric(self):
        """
        method definition to record a new metric value
        """
        try:
            storage.insert(self)
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            raise

    @staticmethod
    def fetch_metrics(user_id=None, metric_type=None):
        """
        method definition to fetch metrics
        based on user id or metric type
        """
        try:
            query = storage.query(Analytics)
            if user_id:
                query = query.filter_by(user_id=user_id)
            if metric_type:
                query = query.filter_by(metric_type=metric_type)
            return query.all()
        except Exception as e:
            logging.error(f"Failed to fetch metrics: {e}")
            raise

    @staticmethod
    def analyze_trends():
        """
        method definition to analyze trends
        from collected metrics over a specified time period
        """
        try:
            if time_period.endswith('d'):
                days = int(time_period[:-1])
                start_date = datetime.now(pytz.timezone('Africa/Nairobi')) - timedelta(days=days)
            else:
                raise ValueError("Unsupported time period format.")

            results = (
                    storage.query(Analytics.metric_type, func.avg(Analytics.metric_value).label('average_value'))
                    .filter(Analytics.timestamp >= start_date)
                    .group_by(Analytics.metric_type)
                    .all()
                    )

            trends = {
                    "time_period": time_period,
                    "start_date": start_date.isoformat(),
                    "trends": {result.metric_type: result.average_value for result in results}
                    }
            return trends
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            raise

    @staticmethod
    def export_data(file_format='json', file_path='analytics_export'):
        """
        method definition that exports data in a specified file format
        """
        try:
            data = storage.query(Analytics).all()
            data_dicts = [
                    {
                        "analytics_id": record.analytics_id,
                        "user_id": record.user_id,
                        "task_id": record.task_id,
                        "metric_type": record.metric_type,
                        "metric_value": record.metric_value,
                        "timestamp": record.timestamp.isoformat(),
                        "report_data": record.report_data
                        }
                    for record in data
                    ]
            if file_format == 'json':
                with open(f"{file_path}.json", 'w') as json_file:
                    json.dump(data_dicts, json_file, indent=4)
            elif file_format == 'csv':
                with open(f"{file_path}.csv", 'w', newline='') as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=data_dicts[0].keys())
                    writer.writeheader()
                    writer.writerows(data_dicts)
            else:
                raise ValueError("unsupported file format. Use json/csv'.")
        
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise
