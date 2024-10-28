#!/usr/bin/env python3
"""
these are the routes for the audit logs model
"""
import logging
from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
from models.audit_logs imprt AuditLog

audit_log = blueprint('audit_log_bp', __name__)
logger = logging.getLogger(__name__)

@audit_log_bp.route('/log_action', methods=['POST'])
def log_action():
    data = request.json
    required_fields = ['user_id', 'action_type', 'entity_type', 'entity_id']

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    audit_log = AuditLog(
        user_id=data['user_id'],
        action_type=data['action_type'],
        entity_type=data['entity_type'],
        entity_id=data['entity_id'],
        details=data.get('details'),
        ip_address=data.get('ip_address'),
        status=data.get('status', 'success')
    )

    try:
        audit_log.log_action()
        return jsonify({"message": "Action logged successfully"}), 201
    except Exception as e:
        logger.error(f"Failed to log action: {e}")
        return jsonify({"error": "Failed to log action"}), 500

@audit_log_bp.route('/fetch_logs', methods=['GET'])
def fetch_logs():
    user_id = request.args.get('user_id')
    entity_type = request.args.get('entity_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    date_range = None

    if start_date and end_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            date_range = (start_date, end_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format"}), 400

    try:
        logs = AuditLog.fetch_logs(user_id=user_id, entity_type=entity_type, date_range=date_range)
        return jsonify([log.serialize() for log in logs]), 200
    except Exception as e:
        logger.error(f"Failed to fetch logs: {e}")
        return jsonify({"error": "Failed to fetch logs"}), 500

@audit_log_bp.route('/search_logs', methods=['GET'])
def search_logs():
    keyword = request.args.get('keyword')

    if not keyword:
        return jsonify({"error": "Keyword is required"}), 400

    try:
        logs = AuditLog.search_logs(keyword)
        return jsonify([log.serialize() for log in logs]), 200
    except Exception as e:
        logger.error(f"Failed to search logs: {e}")
        return jsonify({"error": "Failed to search logs"}), 500

@audit_log_bp.route('/export_logs', methods=['GET'])
def export_logs():
    file_format = request.args.get('format', 'csv')
    try:
        file_path = AuditLog.export_logs(file_format)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"Failed to export logs: {e}")
        return jsonify({"error": "Failed to export logs"}), 500

@audit_log_bp.route('/generate_summary', methods=['GET'])
def generate_summary():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    time_period = None

    if start_date and end_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            time_period = (start_date, end_date)
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format"}), 400

    try:
        summary = AuditLog.generate_summary(time_period)
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Failed to generate summary: {e}")
        return jsonify({"error": "Failed to generate summary"}), 500
