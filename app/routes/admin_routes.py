#!/usr/bin/env python3

"""
these are the routes for the admin model
"""
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from storage import Storage
from models.admin import Admin
import logging

admin_bp = Blueprint('admin', __name__)
storage = Storage()

@admin_bp.route('/admins', methods=['POST'])
def create_admin():
    try:
        data = request.get_json()
        admin = Admin(
            username=data['username'],
            email=data['email']
        )
        admin.set_password(data['password'])
        storage.add(admin)
        return jsonify({'message': 'Admin created successfully'}), 201
    except Exception as e:
        logging.error(f"Error creating admin: {e}")
        return jsonify({'error': 'Failed to create admin'}), 500

@admin_bp.route('/admins/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    try:
        admin = storage.get(Admin, admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        return jsonify({
            'admin_id': admin.admin_id,
            'username': admin.username,
            'email': admin.email,
            'created_date': admin.created_date,
            'last_login': admin.last_login,
            'is_active': admin.is_active
        }), 200
    except Exception as e:
        logging.error(f"Error fetching admin: {e}")
        return jsonify({'error': 'Failed to retrieve admin'}), 500

@admin_bp.route('/admins/<int:admin_id>', methods=['PUT'])
def update_admin(admin_id):
    try:
        data = request.get_json()
        admin = storage.get(Admin, admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404

        admin.username = data.get('username', admin.username)
        admin.email = data.get('email', admin.email)
        if 'password' in data:
            admin.set_password(data['password'])
        storage.update(admin)
        return jsonify({'message': 'Admin updated successfully'}), 200
    except Exception as e:
        logging.error(f"Error updating admin: {e}")
        return jsonify({'error': 'Failed to update admin'}), 500

@admin_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
def delete_admin(admin_id):
    try:
        admin = storage.get(Admin, admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        storage.delete(admin)
        return jsonify({'message': 'Admin deleted successfully'}), 200
    except Exception as e:
        logging.error(f"Error deleting admin: {e}")
        return jsonify({'error': 'Failed to delete admin'}), 500

@admin_bp.route('/admins/<int:admin_id>/activate', methods=['POST'])
def activate_admin(admin_id):
    try:
        admin = storage.get(Admin, admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        admin.is_active = True
        storage.update(admin)
        return jsonify({'message': 'Admin activated successfully'}), 200
    except Exception as e:
        logging.error(f"Error activating admin: {e}")
        return jsonify({'error': 'Failed to activate admin'}), 500

@admin_bp.route('/admins/<int:admin_id>/deactivate', methods=['POST'])
def deactivate_admin(admin_id):
    try:
        admin = storage.get(Admin, admin_id)
        if not admin:
            return jsonify({'error': 'Admin not found'}), 404
        admin.is_active = False
        storage.update(admin)
        return jsonify({'message': 'Admin deactivated successfully'}), 200
    except Exception as e:
        logging.error(f"Error deactivating admin: {e}")
        return jsonify({'error': 'Failed to deactivate admin'}), 500
