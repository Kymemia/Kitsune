#!/usr/bin/env python3

"""
these are the routes for the analytics model
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from models.analytics import Analytics

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/record', methods=['POST'])
def record_metric():
    """
    Route to record a new metric value.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    metric = Analytics(
        user_id=data.get('user_id'),
        task_id=data.get('task_id'),
        metric_type=data.get('metric_type'),
        metric_value=data.get('metric_value'),
        timestamp=datetime.now()
    )

    try:
        metric.record_metric()
        return jsonify({'message': 'Metric recorded successfully'}), 201
    except SQLAlchemyError as e:
        return jsonify({'error': f'Failed to record metric: {str(e)}'}), 500

@analytics_bp.route('/fetch', methods=['GET'])
def fetch_metrics():
    """
    Route to fetch metrics based on user_id and/or metric_type.
    """
    user_id = request.args.get('user_id')
    metric_type = request.args.get('metric_type')

    try:
        metrics = Analytics.fetch_metrics(user_id=user_id, metric_type=metric_type)
        metrics_data = [
            {
                "analytics_id": metric.analytics_id,
                "user_id": metric.user_id,
                "task_id": metric.task_id,
                "metric_type": metric.metric_type,
                "metric_value": metric.metric_value,
                "timestamp": metric.timestamp.isoformat(),
                "report_data": metric.report_data
            } for metric in metrics
        ]
        return jsonify(metrics_data), 200
    except SQLAlchemyError as e:
        return jsonify({'error': f'Failed to fetch metrics: {str(e)}'}), 500

@analytics_bp.route('/analyze', methods=['GET'])
def analyze_trends():
    """
    Route to analyze trends over a specified time period.
    """
    time_period = request.args.get('time_period', '7d')

    try:
        trends = Analytics.analyze_trends(time_period)
        return jsonify(trends), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': f'Failed to analyze trends: {str(e)}'}), 500

@analytics_bp.route('/export', methods=['GET'])
def export_data():
    """
    Route to export analytics data in JSON or CSV format.
    """
    file_format = request.args.get('file_format', 'json')
    file_path = request.args.get('file_path', 'analytics_export')

    try:
        Analytics.export_data(file_format=file_format, file_path=file_path)
        return jsonify({'message': f'Data exported successfully to {file_path}.{file_format}'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except SQLAlchemyError as e:
        return jsonify({'error': f'Failed to export data: {str(e)}'}), 500
