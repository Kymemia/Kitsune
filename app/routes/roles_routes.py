#!/usr/bin/env python3

"""
these are the routes for the roles model
"""
from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from models.engine.user import User
from models.roles import Role

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles', methods=['POST'])
def create_role():
    data = request.json
    role_name = data.get('name')
    with db.session.begin():
        role = Role.create_role(db.session, role_name)
    return jsonify({"id": role.id, "name": role.name}), 201

@roles_bp.route('/roles/<string:role_name>', methods=['DELETE'])
def delete_role(role_name):
    with db.session.begin():
        success = Role.delete_role(db.session, role_name)
    return jsonify({"success": success}), 204

@roles_bp.route('/roles/<string:role_name>/permissions', methods=['POST'])
def assign_permission_to_role(role_name):
    data = request.json
    permission_name = data.get('permission')
    with db.session.begin():
        success = Role.assign_permission_to_role(db.session, role_name, permission_name)
    return jsonify({"success": success}), 200

@roles_bp.route('/users/<string:user_id>/roles', methods=['POST'])
def assign_role_to_user(user_id):
    data = request.json
    role_name = data.get('role')
    with db.session.begin():
        success = Role.assign_role_to_user(db.session, user_id, role_name)
    return jsonify({"success": success}), 200
