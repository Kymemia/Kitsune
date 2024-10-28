#!/usr/bin/env python3

"""
this is the roles model for our platform
"""
import logging
from user import Base
from sqlalchemy import Column, Integer, String, ForeignKey
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
    __tablename__ = "roles"

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
        """
        method definition that assigns a specific role to a user in the system by querying the DB for the user & role based on user_id and role_name.
        If they both exist, the user's role is updated, and the change is committed to the DB

        Args:
            session (Session): SQLAlchemy session instance for interacting with the DB
            user_id (str): user's unique id that will be assigned a role
            role_name (str): specific role to be assigned

        Returns:
            bool: True should the role be successfully assigned. Else, false

        Raises:
            SQLAlchemyError: Should an error occur while querying the DB
        """
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
        method definition that sets & returns the role of a user
        based on their user ID

        It queries the DB to retrieve the user associated with the user_id and returns their role

        Appropriate exceptions are raised if user does not exist or an error occurs

        Args:
            session: SQLAlchemy session to interact with the DB
            user_id: user's unique ID whose role needs to be set

        Returns:
            str or None: Returns role assigned to a user if found
                        Else, returns None

        Raises:
            SQLAlchemyError: should an error occur
                        while interacting with the DB
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
        method definition that performs a specific action
        if the user has the required permission.
        It checks the user's roles and verifies if the user
        has the necessary permission to execute said action.

        Args:
            session: SQLAlchemy session to interact with the DB
            user_id (str): user's ID whose permissions are checked
            action (function): the action that needs to be performed
            if the user has correct permission
            *args: positional arguments to pass the action function
            **kwargs: keyword arguments to pass to the action function

        Returns:
            Any: the result of the action if the user has permission
                and the action returns a value


        Raises:
            PermissionError: should the user not have permission
                    to perform the action
            SQLAlchemyError: should a problem occur while querying the DB
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
