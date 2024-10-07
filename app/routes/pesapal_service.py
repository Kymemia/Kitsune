#!/usr/bin/env python3

"""
routes necessary for pesapal integration
"""

from flask import Blueprint, request, jsonify
from services.pesapal_service import PesaPalService

pesapal_blueprint = Blueprint('pesapal', __name__)

pesapal_service = PesaPalService()

@pesapal_blueprint.route('/test')
def test_route():
    return "Pesapal route is working"


@pesapal_blueprint.route('/pesapal/initiate-payment', methods=['POST'])
def initiate_payment():
    try:
        order_data = request.json
        if not order_data or 'order_id' not in order_data:
            return jsonify({'error': 'Invalid order data'}), 400

        response = pesapal_service.initiate_payment(order_data)
        return jsonify(response), 200
    except ValueError as ve:
        logging.error(f"ValueError: {ve}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        logging.error(f"Failed to initiate payment: {e}")
        return jsonify({'error': str(e)}), 500


@pesapal_blueprint.route('/pesapal/check-transaction-status/<transaction_id>', methods=['GET'])
def check_transaction_status(transaction_id):
    try:
        response = pesapal_service.check_transaction_status(transaction_id)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pesapal_blueprint.route('/pesapal/confirm-payment/<transaction_id>', methods=['GET'])
def confirm_payment(transaction_id):
    try:
        response = pesapal_service.confirm_payment(transaction_id)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pesapal_blueprint.route('/pesapal/process-refund', methods=['POST'])
def process_refund():
    try:
        refund_data = request.json
        payment_id = refund_data['payment_id']
        amount = refund_data['amount']
        reason = refund_data['reason']
        response = pesapal_service.process_refund(payment_id, amount, reason)
        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
