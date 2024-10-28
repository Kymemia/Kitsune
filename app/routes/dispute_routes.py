#!/usr/bin/env python3

"""
these are the routes for the dispute model
"""
from flask import Blueprint, request, jsonify
from models.disputes import Dispute, DisputeStatus
from models import db

dispute_bp = Blueprint('dispute_routes', __name__)

@dispute_bp.route('/dispute', methods=['POST'])
def create_dispute():
    data = request.json
    new_dispute = Dispute(
        task_id=data.get('task_id'),
        poster_id=data.get('poster_id'),
        tasker_id=data.get('tasker_id'),
        reason=data.get('reason'),
        description=data.get('description')
    )
    db.session.add(new_dispute)
    db.session.commit()
    return jsonify({"message": "Dispute created successfully"}), 201

@dispute_bp.route('/dispute/<int:dispute_id>/evidence', methods=['PUT'])
def submit_evidence(dispute_id):
    dispute = Dispute.query.get(dispute_id)
    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404
    evidence = request.json.get('evidence')
    dispute.submit_evidence(evidence)
    return jsonify({"message": "Evidence submitted successfully"}), 200

@dispute_bp.route('/dispute/<int:dispute_id>/status', methods=['PUT'])
def update_status(dispute_id):
    dispute = Dispute.query.get(dispute_id)
    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404
    new_status = request.json.get('status')
    if new_status in DisputeStatus.__members__:
        dispute.update_status(DisputeStatus[new_status])
        return jsonify({"message": "Dispute status updated"}), 200
    return jsonify({"error": "Invalid status"}), 400

@dispute_bp.route('/dispute/<int:dispute_id>/resolve', methods=['PUT'])
def resolve_dispute(dispute_id):
    dispute = Dispute.query.get(dispute_id)
    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404
    outcome = request.json.get('outcome')
    dispute.resolve_dispute(outcome)
    return jsonify({"message": "Dispute resolved"}), 200

@dispute_bp.route('/dispute/<int:dispute_id>/escalate', methods=['PUT'])
def escalate_dispute(dispute_id):
    dispute = Dispute.query.get(dispute_id)
    if not dispute:
        return jsonify({"error": "Dispute not found"}), 404
    dispute.escalate_dispute()
    return jsonify({"message": "Dispute escalated"}), 200

@dispute_bp.route('/dispute/<int:dispute_id>/history', methods=['GET'])
def fetch_dispute_history(dispute_id):
    history = Dispute.fetch_dispute_history(dispute_id)
    if not history:
        return jsonify({"error": "Dispute not found"}), 404
    return jsonify(history), 200
