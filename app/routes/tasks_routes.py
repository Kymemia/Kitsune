#!/usr/bin/env python3

"""
these are the routes for the task model
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from datetime import datetime
from models.tasks import Task, TaskStatusEnum, TaskPriorityEnum
from models.user import User
from models.attachment import Attachment
from models.notification import NotificationModel
from models.audit_log import AuditLog
from models.review import Review
from extensions import db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    creator_id = data.get('creator_id')
    location_id = data.get('location_id')
    payment_amount = data.get('payment_amount')
    due_date = data.get('due_date')
    priority = data.get('priority', TaskPriorityEnum.MEDIUM.value)

    try:
        new_task = Task(
            title=title,
            description=description,
            creator_id=creator_id,
            location_id=location_id,
            payment_amount=payment_amount,
            due_date=datetime.fromisoformat(due_date) if due_date else None,
            priority=TaskPriorityEnum(priority)
        )
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'message': 'Task created successfully', 'task_id': new_task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating task: {str(e)}'}), 500

@tasks_bp.route('/tasks/<int:task_id>/assign', methods=['POST'])
def assign_task(task_id):
    data = request.json
    tasker_id = data.get('tasker_id')

    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        task.assign_tasker(db.session, tasker_id)
        return jsonify({'message': 'Tasker assigned successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error assigning tasker: {str(e)}'}), 500

@tasks_bp.route('/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    new_status = data.get('status')

    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        task.change_status(db.session, TaskStatusEnum(new_status))
        return jsonify({'message': 'Task status updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error updating task status: {str(e)}'}), 500

@tasks_bp.route('/tasks/<int:task_id>/cancel', methods=['PUT'])
def cancel_task(task_id):
    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        task.cancel_task(db.session)
        return jsonify({'message': 'Task canceled successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Error canceling task: {str(e)}'}), 500

@tasks_bp.route('/tasks/<int:task_id>/attachments', methods=['POST'])
def add_attachment(task_id):
    data = request.json
    attachment_data = data.get('attachment')

    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        attachment = Attachment(data=attachment_data, task_id=task.id)
        task.add_attachment(db.session, attachment)
        return jsonify({'message': 'Attachment added successfully'}), 201
    except Exception as e:
        return jsonify({'error': f'Error adding attachment: {str(e)}'}), 500

@tasks_bp.route('/tasks/<int:task_id>/history', methods=['GET'])
def get_task_history(task_id):
    task = db.session.query(Task).get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    try:
        history = task.fetch_task_history(db.session)
        return jsonify([{
            'attribute': entry.attribute,
            'old_value': entry.old_value,
            'new_value': entry.new_value,
            'change_date': entry.change_date.isoformat()
        } for entry in history]), 200
    except Exception as e:
        return jsonify({'error': f'Error fetching task history: {str(e)}'}), 500
