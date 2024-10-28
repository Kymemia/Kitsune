#!/usr/bin/env python3

"""
these are the routes for the support model
"""
import logging
from flask import Blueprint, request, jsonify
from models.support import SupportTicket, TicketStatus, PriorityLevel
from datetime import datetime

support_bp = Blueprint('support', __name__)

@support_bp.route('/create', methods=['POST'])
def create_ticket():
    data = request.get_json()
    user_id = data.get('user_id')
    subject = data.get('subject')
    description = data.get('description')
    category = data.get('category')
    priority_level = data.get('priority_level')

    if not all([user_id, subject, description, category, priority_level]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            description=description,
            category=Category[category.upper()],
            priority_level=PriorityLevel[priority_level.upper()]
        )
        ticket.create_ticket(user_id, subject, description, Category[category.upper()], PriorityLevel[priority_level.upper()])

        session.add(ticket)
        session.commit()

        return jsonify({'message': 'Ticket created successfully', 'ticket_id': ticket.ticket_id}), 201
    except Exception as e:
        logging.error(f"Error creating ticket: {e}")
        return jsonify({'error': 'Failed to create ticket'}), 500

@support_bp.route('/assign/<int:ticket_id>', methods=['POST'])
def assign_ticket(ticket_id):
    data = request.get_json()
    support_agent_id = data.get('support_agent_id')

    if not support_agent_id:
        return jsonify({'error': 'Missing support agent ID'}), 400

    ticket = session.query(SupportTicket).get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        ticket.assign_ticket(support_agent_id)
        session.commit()
        return jsonify({'message': 'Ticket assigned successfully'}), 200
    except Exception as e:
        logging.error(f"Error assigning ticket: {e}")
        return jsonify({'error': 'Failed to assign ticket'}), 500

@support_bp.route('/update_status/<int:ticket_id>', methods=['POST'])
def update_ticket_status(ticket_id):
    data = request.get_json()
    new_status = data.get('new_status')

    ticket = session.query(SupportTicket).get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        ticket.update_ticket_status(TicketStatus[new_status.upper()])
        session.commit()
        return jsonify({'message': 'Ticket status updated successfully'}), 200
    except Exception as e:
        logging.error(f"Error updating ticket status: {e}")
        return jsonify({'error': 'Failed to update ticket status'}), 500

@support_bp.route('/close/<int:ticket_id>', methods=['POST'])
def close_ticket(ticket_id):
    ticket = session.query(SupportTicket).get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        ticket.close_ticket()
        session.commit()
        return jsonify({'message': 'Ticket closed successfully'}), 200
    except Exception as e:
        logging.error(f"Error closing ticket: {e}")
        return jsonify({'error': 'Failed to close ticket'}), 500

@support_bp.route('/history/<int:ticket_id>', methods=['GET'])
def fetch_ticket_history(ticket_id):
    ticket = session.query(SupportTicket).get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404

    try:
        history = ticket.fetch_ticket_history()
        return jsonify([{
            'status': entry.status,
            'updated_at': entry.updated_at,
            'notes': entry.notes
        } for entry in history]), 200
    except Exception as e:
        logging.error(f"Error fetching ticket history: {e}")
        return jsonify({'error': 'Failed to fetch ticket history'}), 500
