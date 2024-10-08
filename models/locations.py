#!/usr/bin/env python3

"""
this is the locations model for our platform
"""
import pytz
import numpy as np
from sklearn.cluser import DBSCAN
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, FreignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
EAT = pytz.timezone('Africa/Nairobi')


class Location(Base):
    """
    class definition containing all the key attributes
    and methods for the locations model
    """
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    latitude: float = Column(Float, nullable=False, index=True)
    longitude: float = Column(Float, nullable=False, index=True)
    address: str = Column(String(255), nullable=True)
    task_id: int = Column(Integer, ForeignKey('tasks.id'), nullable=True)
    radius: float = Column(Float, default=18.0)
    created_at: datetime = Column(DateTime, default=lambda: datetime.now(EAT))
    updated_at: datetime = Column(DateTime, default=lambda: datetime.now(EAT))

    user = relationship('User', back_populates='locations')
    task = relationship('Task', back_populates='locations')

    def __repr__(self):
        """
        print out all important information regarding user's current location
        """
        return f"<Location(id={self.id}, user_id={self.user_id}, latitude={self.latitude}, longitude={self.longitude}, radius={self.radius})>"

    def create_location(
            self, user_id: int,
            latitude: float, longitude: float,
            address: str ='', radius: float = 18.0
            ):
        """
        method definition to create a new location
        default radius is set at 18KM
        """
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.radius = radius
        self.created_at = datetime.now(EAT)
        self.updated_at = datetime.now(EAT)

    def update_location(
            self, latitude: float = None,
            longitude: float = None, address: str = None,
            radius: float = None
            ):
        """
        method definition to update user's location details
        """
        if latitude:
            self.latitude = latitude
        if longitude:
            self.longitude = longitude
        if address:
            self.address = address
        if radius:
            self.radius = radius
        self.updated_at = datetime.now(EAT)

    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        method definition to calculate the distance between two
        geographic points using the Haversine formula
        """
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2))
        c = 2 * atan2(sqrt(a), sqrt(1 -a))
        return R * c

    @classmethod
    def find_nearby_tasks(
            cls, session,
            current_latitude: float,
            current_longitude: float, radius: float
            ):
        """
        method definition that finds tasks within a specific radius
        of the user's current location
        """
        tasks = session.query(Task).all()
        nearby_tasks = []
        for task in tasks:
            distance = cls.calculate_distance(current_latitude, current, longitude, task.location.latitude, task.location.longitude)
            if distance <= radius:
                nearby_tasks.append(task)
        return nearby_tasks

    @classmethod
    def fetch_locations(cls, session, user_id: int = None, task_id: int = None):
        """
        method definition to fetch locations based on user ID or task ID
        """
        query = session.query(cls)
        if user_id:
            query = query.filter(cls.user_id == user_id)
        if task_id:
            query = query.filter(cls.task_id == task_id)
        return query.all()

    @classmethod
    def cluster_locations(cls, session):
        """
        method definition to cluster locations based
        on latitude and longitude to show density
        of tasks in certain areas
        """
        locations = session.query(cls).all()
        coords = np.array([(loc.latitude, loc.longitude) for loc in locations])

        clustering = DBSCAN(eps=0.01, min_samples=5).fit(coords)
        return clustering.labels_

    # Possible features to implement(discussion needed):
    # *Redis for caching
    # *heatmaps - show areas where tasks are frequently posted
