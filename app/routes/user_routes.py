#!/usr/bin/env python3
"""
these are the routes for the user model
"""
from flask import Blueprint, request, jsonify
from werkzeug.exceptions import NotFound, BadRequest
from sqlalchemy.orm import Session
from models.user import User
from models.engine.storage import db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.json
    required_fields = ['username', 'email', 'hashed_password']

    for field in required_fields:
        if field not in data:
            raise BadRequest(f"Missing required field: {field}")

    user = User(
        username=data['username'],
        email=data['email'],
        hashed_password=data['hashed_password'],
        firstname=data.get('firstname'),
        lastname=data.get('lastname'),
        age=data.get('age'),
        phone_number=data.get('phone_number'),
        user_type=data.get('user_type', 'user'),
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user.to_dict()), 201


@user_bp.route('/users/<string:uid>', methods=['GET'])
def get_user(uid):
    """Retrieve a user by UID."""
    user = db.session.query(User).filter_by(uid=uid).first()

    if user is None:
        raise NotFound("User not found")

    return jsonify(user.to_dict())


@user_bp.route('/users/<string:uid>', methods=['PUT'])
def update_user(uid):
    """Update user information."""
    user = db.session.query(User).filter_by(uid=uid).first()

    if user is None:
        raise NotFound("User not found")

    data = request.json
    for key, value in data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.session.commit()
    return jsonify(user.to_dict())


@user_bp.route('/users/<string:uid>', methods=['DELETE'])
def delete_user(uid):
    """Delete a user."""
    user = db.session.query(User).filter_by(uid=uid).first()

    if user is None:
        raise NotFound("User not found")

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 204
