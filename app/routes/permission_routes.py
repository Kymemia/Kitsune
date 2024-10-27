#!/usr/bin/env python3
"""
these are the routes for the permissions model
"""
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from storage import session
from permissions import Permission
from user import User
import logging

permissions_bp = Blueprint('permissions', __name__)

@permissions_bp.route('/register', methods=['POST'])
def register_permission():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        role_id = data.get('role_id')
        
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        permission = Permission(
            user_id=user_id,
            role_id=role_id,
            can_create=data.get('can_create', False),
            can_read=data.get('can_read', False),
            can_update=data.get('can_update', False),
            can_delete=data.get('can_delete', False),
            can_override=data.get('can_override', False),
            active=data.get('active', True)
        )
        
        session.add(permission)
        session.commit()
        
        return jsonify({'message': 'Permission registered successfully.'}), 201

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error registering permission: {e}")
        return jsonify({'error': 'An error occurred while registering permission.'}), 500

@permissions_bp.route('/update/<int:permission_id>', methods=['PUT'])
def update_permission(permission_id):
    try:
        data = request.get_json()
        permission = session.query(Permission).filter_by(id=permission_id).first()
        
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404

        permission.can_create = data.get('can_create', permission.can_create)
        permission.can_read = data.get('can_read', permission.can_read)
        permission.can_update = data.get('can_update', permission.can_update)
        permission.can_delete = data.get('can_delete', permission.can_delete)
        permission.can_override = data.get('can_override', permission.can_override)
        permission.active = data.get('active', permission.active)
        
        session.commit()
        permission.audit_permissions()
        
        return jsonify({'message': 'Permission updated successfully.'}), 200

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error updating permission: {e}")
        return jsonify({'error': 'An error occurred while updating permission.'}), 500

@permissions_bp.route('/revoke/<int:permission_id>', methods=['PUT'])
def revoke_permission(permission_id):
    try:
        data = request.get_json()
        permission_type = data.get('permission_type')

        permission = session.query(Permission).filter_by(id=permission_id).first()
        if not permission:
            return jsonify({'error': 'Permission not found'}), 404

        permission.revoke_permission(permission_type)
        session.commit()
        permission.audit_permissions()

        return jsonify({'message': f'{permission_type} permission revoked successfully.'}), 200

    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error revoking permission: {e}")
        return jsonify({'error': 'An error occurred while revoking permission.'}), 500

@permissions_bp.route('/<int:user_id>', methods=['GET'])
def view_permissions(user_id):
    try:
        permissions = session.query(Permission).filter_by(user_id=user_id).all()
        if not permissions:
            return jsonify({'error': 'No permissions found for the user'}), 404

        permissions_data = [permission.get_permissions() for permission in permissions]
        return jsonify({'permissions': permissions_data}), 200

    except SQLAlchemyError as e:
        logging.error(f"Error fetching permissions: {e}")
        return jsonify({'error': 'An error occurred while fetching permissions.'}), 500
