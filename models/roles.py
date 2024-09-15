#!/usr/bin/env python3

"""
this is the roles model for our platform
"""
import logging
from user import Base
from sqlalchemy import Column, Integer, String, ForeginKey
from sqlalchemy.orm import relationship, Session
from sqlalchemy.exc import SQLAlchemyError


role_permissions = Table(
        "role_permissions",
        Base.metadata,
        Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
        Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True)
        )


class Role(Base):
    """
    class definition containing all the key methods
    & attributes for the role model
    """
    __tablename_) = "roles"

    id = Column(Integer, primary_key=True)
    name = COlumn(String, nullable=False, unique=True)
    permissions = relationship("Permission", secondary=role_permissions, back populates="roles")

    def __repr__(self):
        """
        method definition to display key information
        regarding roles assigned to a certain user
        """
        return f"<Role(id={self.id}, name={self.name})>"

    @staticmethod
    def create_role(session: Session, role_name: str):
        """
        method definition to create a role
        """
        try:
            new_role = Role(name=role_name)
            session.add(new_role)
            session.commit()
            return new_role
        except SQLAlchemyError as e:
            logging.error(f"Error creating role: {e}")
            session.rollback()
            raise

    @staticmethod
    def delete_role(session: Session, role_name: str):
        """
        method definition to delete a role
        """
        try:
            role = session.query(Role).filter_by(name=role_name).first()
            if role:
                session.delete(role)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error deleting role: {e}")
            session.rollback()
            raise

    @staticmethod
    def create_permission(session: Session, permission_name: str):
        """
        method definition to create custom permissions
        """
        try:
            new_permission = Permission(name=permission_name)
            session.add(new_permission)
            session.commit()
            return new_permission
        except SQLAlchemyError as e:
            logging.error(f"Error creating permission: {e}")
            session.rollback()
            raise

    @staticmethod
    def assign_permission_to_role(session: Session, role_name: str, permission_name: str):
        """
        method definition that assigns custom permission
        to a certain role
        """
        try:
            role = session.query(Role).filter_by(name=role_name).first()
            permission = session.query(Permission).filter_by(name=permission_name).first()
            if role and permission:
                role.permissions.append(permission)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error assigning permission to role: {e}")
            session.rollback()
            raise

    @staticmethod
    def assign_role_to_user(session: Session, user_id: str, role_name: str):
        try:
            role = session.query(Role).filter_by(name=role_name).first()
            user = session.query(User).filter_by(uid=user_id).first()
            if role and user:
                user.role = role
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            logging.error(f"Error assigning role to user: {e}")
            session.rollback()
            raise

    @staticmethod
    def check_permission(session: Session, user_id: str, permission_name: str):
        """
        method definition to check which permissions
        are granted to a user
        """
        try:
            user = session.query(User).filter_by(uid=user_id).first()
            if user:
                role = user.role
                if role and any(p.name == permission_name for p in role.permissions):
                    return True
                return False
            except SQLAlchemyError as e:
                logging.error(f"Error checking permission: {e}")
                raise

    @staticmethod
    def set_current_user_role(session: Session, user_id: str):
        """
        """
        try:
            user = session.query(User).filter_by(uid=user_id).first()
            if user:
                return user.role
            return None
        except SQLAlchemyError as e:
            logging.erro(f"Error setting user role: {e}")
            raise

    @staticmethod
    def perform_action(session: Session, user_id: str, action, *args, **kwargs):
        """
        """
        try:
            role = Role.set_current_user_role(session, user_id)
            if role and Role.check_permission(session, user_id, action.__name__):
                return action(*args, **kwargs)
            else:
                raise PermissionError("User does not have permission to perform this action.")
        except SQLAlchemyError as e:
            logging.error(f"Error performing action: {e}")
            raise
