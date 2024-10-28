#!/usr/bin/env python3
"""
these are the routes for the notification model
"""
import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.notifications import NotificationModel

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/create', methods=['POST'])
def create():
    data = request.get_json()
    user_id = data.get('user_id')
    notification_type = data.get('notification_type')
    content = data.get('content')
    priority = data.get('priority', 'MEDIUM')
    delivery_channel = data.get('delivery_channel', 'IN_APP')

    if not all([user_id, notification_type, content]):
        return jsonify({'error': 'Missing required fields'}), 400

    notification = create_notification(user_id, notification_type, content, priority, delivery_channel)
    return jsonify({'message': 'Notification created', 'notification_id': notification.id})

@notifications_bp.route('/send/<int:notification_id>', methods=['POST'])
def send(notification_id):
    try:
        send_notification(notification_id)
        return jsonify({'message': 'Notification sent successfully'})
    except Exception as e:
        logging.error(f"Error sending notification {notification_id}: {e}")
        return jsonify({'error': 'Failed to send notification'}), 500

@notifications_bp.route('/mark_as_read/<int:notification_id>', methods=['POST'])
def mark_as_read_view(notification_id):
    try:
        mark_as_read(notification_id)
        return jsonify({'message': 'Notification marked as read'})
    except Exception as e:
        logging.error(f"Error marking notification {notification_id} as read: {e}")
        return jsonify({'error': 'Failed to mark as read'}), 500

@notifications_bp.route('/user/<int:user_id>/notifications', methods=['GET'])
def fetch_user_notifications(user_id):
    notifications = fetch_notifications(user_id)
    return jsonify([{
        'notification_id': n.id,
        'content': n.content,
        'status': n.status.value,
        'timestamp': n.timestamp
    } for n in notifications])

@notifications_bp.route('/user/<int:user_id>/history', methods=['GET'])
def notification_history_view(user_id):
    history = notification_history(user_id)
    return jsonify([{
        'notification_id': n.id,
        'content': n.content,
        'status': n.status.value,
        'timestamp': n.timestamp
    } for n in history])

@notifications_bp.route('/user/<int:user_id>/bell', methods=['GET'])
def notifications_bell_view(user_id):
    bell_data = get_notifications_bell(user_id)
    return jsonify(bell_data)

@notifications_bp.route('/user/<int:user_id>/messages_icon', methods=['GET'])
def messages_icon_view(user_id):
    messages_icon_data = get_messages_icon(user_id)
    return jsonify(messages_icon_data)
