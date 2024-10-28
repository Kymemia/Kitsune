#!/usr/bin/env python3
"""
these are the routes for the location model
"""
# location_routes.py

from flask import Blueprint, request, jsonify
from models import db
from models.locations import Location
from models.task import Task

location_bp = Blueprint('location', __name__, url_prefix='/locations')

@location_bp.route('/create', methods=['POST'])
def create_location():
    data = request.get_json()
    user_id = data.get('user_id')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address = data.get('address', '')
    radius = data.get('radius', 18.0)

    location = Location()
    location.create_location(user_id, latitude, longitude, address, radius)

    db.session.add(location)
    db.session.commit()

    return jsonify({'message': 'Location created successfully', 'location_id': location.id}), 201

@location_bp.route('/update/<int:location_id>', methods=['PUT'])
def update_location(location_id):
    location = Location.query.get(location_id)
    if not location:
        return jsonify({'error': 'Location not found'}), 404

    data = request.get_json()
    location.update_location(
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        address=data.get('address'),
        radius=data.get('radius')
    )
    db.session.commit()

    return jsonify({'message': 'Location updated successfully'})

@location_bp.route('/fetch', methods=['GET'])
def fetch_locations():
    user_id = request.args.get('user_id', type=int)
    task_id = request.args.get('task_id', type=int)

    locations = Location.fetch_locations(db.session, user_id, task_id)
    return jsonify([{
        'id': loc.id,
        'latitude': loc.latitude,
        'longitude': loc.longitude,
        'address': loc.address,
        'radius': loc.radius,
        'created_at': loc.created_at,
        'updated_at': loc.updated_at
    } for loc in locations])

@location_bp.route('/nearby-tasks', methods=['GET'])
def find_nearby_tasks():
    current_latitude = request.args.get('latitude', type=float)
    current_longitude = request.args.get('longitude', type=float)
    radius = request.args.get('radius', type=float, default=18.0)

    nearby_tasks = Location.find_nearby_tasks(db.session, current_latitude, current_longitude, radius)
    return jsonify([{
        'task_id': task.id,
        'task_name': task.name,
        'latitude': task.location.latitude,
        'longitude': task.location.longitude
    } for task in nearby_tasks])

@location_bp.route('/cluster', methods=['GET'])
def cluster_locations():
    clusters = Location.cluster_locations(db.session)
    return jsonify({'clusters': clusters.tolist()})
