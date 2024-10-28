#!/usr/bin/env python3
"""
these are the routes for the messaging model
"""
import logging
from flask import Blueprint, request, jsonify
from models.messaging import Message, MessageThread

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    task_id = data.get('task_id')
    content = data.get('content')
    attachments = data.get('attachments', None)

    if not (sender_id and receiver_id and task_id and content):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        new_message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            task_id=task_id,
            message_content=content,
            attachments=attachments
        )
        new_message.send_message(receiver_id, content, attachments)
        db.session.commit()
        return jsonify({"message": "Message sent successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error sending message: {e}")
        return jsonify({"error": "Message could not be sent"}), 500

@messaging_bp.route('/fetch_messages/<int:thread_id>', methods=['GET'])
def fetch_messages(thread_id):
    try:
        messages = Message.fetch_messages(thread_id)
        return jsonify([msg.to_dict() for msg in messages]), 200
    except Exception as e:
        logging.error(f"Error fetching messages: {e}")
        return jsonify({"error": "Could not fetch messages"}), 500
