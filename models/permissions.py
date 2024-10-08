#!/usr/bin/env python3

"""
this is the permissions model file
it will contain permissions for all the users for our platform
"""
import logging
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError
from user import Base
from storage import session


role_permissions = Table(
        "role_permissions",
        Base.metadata,
        Column("role_id", ForeignKey("roles.id"), primary_key=True),
        Column("permission_id", ForeignKey("permissions.id"), primary_key=True)
        )


class Role(Base):
    """
    class definition for the roles table in the DB.
    """
    __tablename__ = "roles"

    id = Column(Integer, primery_key=True)
    name = Column(String, nullable=False)
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

# user inherits task & poster roles
class Permission(Base):
    """
    class definition containing all necessary methods & attributes
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    can_create = Column(Boolean, default=False)
    can_read = Column(Boolean, default=False)
    can_update = Column(Boolean, default=False)
    can_delete = Column(Boolean, default=False)
    can_override = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def assign_permission(self, permission_type: str, value: bool):
        """
        method definition to assign a specific permission to the user

        Args:
            permisison_type (str): Specific type of permission(create, read, update, delete)
            value (bool): Option on whether or not to grant said permission

        Raises:
            ValueError: Should the permission type be invalid
        """
        try:
            if permission_type == "create":
                return self.can_create
            if permission_type == "read":
                return self.can_read
            if permission_type == "update":
                return self.can_update
            if permission_type == "delete":
                return self.can_delete
            else:
                raise ValueError(f"Invalid permission type: {permission}.")

        except Exception as e:
            logging.error(f"Error checking permission: {e}.")
            raise

    def overrride_permission(self):
        """
        method definition that allows Super Admin to override any permissions

        Raises:
            PermissionError: Should the user not be a Super Admin
        """
        try:
            if not self.can_override:
                raise PermissionError("User does not have override permissions.")
            
        except Exception as e:
            logging.error(f"Error while overriding permission: {e}.")
            raise

    def revoke_permission(self, permission_type: str):
        """
        method definition that revokes a certain permission from the user

        Args:
            permission_type (str): Specific permission to revoke

        Raises:
            ValueError: Should the permission type be invalid
        """
        try:
            self.assign_permission(permission_type, False)
        except Exception as e:
            logging.error(f"Error while revoking permission: {e}.")
            raise

    def get_permissions(self) -> dict:
        """
        method definition to get the current permissions
        assigned to a certain user

        Returns:
            dict: A dictionary of permission types & their alues
        """
        try:
            return {
                    "create": self.can_create,
                    "read": self.can_read,
                    "update": self.can_update,
                    "delete": self.can_delete,
                    "override": self.can_override,
                    "active": self.active
                    }
        except SQLAlchemyError as e:
            logging.error(f"Error fetching permissions: {e}.")
            raise

    def audit_permissions(self):
        """
        method definition to log changes
        to the user's permissions for audit purposes.
        """
        try:
            logging.info(f"Permissions updated for user_id {self.user_id}.")
        except Exception as e:
            logging.error(f"Error auditing permissions: {e}.")
            raise
