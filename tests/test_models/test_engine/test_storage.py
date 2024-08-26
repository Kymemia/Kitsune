"""
Functions:
    - storage(): Test fixture for the Storage class.
    - test_successful_connection(storage): Test if the storage model can establish a connection to the database with valid credentials.
    - test_failed_connection_with_invalid_credentials(storage): Test if the storage model correctly handles failed connection attempts with invalid credentials (e.g., wrong password).
    - test_connection_timeout(storage): Test how the storage model handles connection timeouts.
    - test_disconnecting_from_database(storage): Test if the storage model can properly disconnect from the database.
    - test_creating_table_users(storage): Test creating the table 'users' in the database.
    - test_inserting_data(storage): Test inserting valid data into a table.
    - test_inserting_data_with_missing_fields(storage): Test inserting data with missing non-nullable fields.
    - test_inserting_duplicate_unique_fields(storage): Test inserting data that violates a unique constraint (e.g., duplicate username).
    - test_updating_data(storage): Test updating existing data in a table.
    - test_updating_non_existent_record(storage): Test updating a record that does not exist.
    - test_deleting_data(storage): Test deleting data from a table.
    - test_deleting_non_existent_record(storage): Test deleting a record that does not exist.
    - test_fetching_single_record(storage): Test fetching a single record using a valid query.
    - test_fetching_all_records(storage): Test fetching all records from a table.
    - test_fetching_with_complex_queries(storage): Test fetching data using complex SQL queries, such as joins and subqueries.
This module contains tests for the Storage class in the engine module.
"""

import os
import logging
from dotenv import load_dotenv
import pytest
from models.engine.storage import Storage
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import OperationalError
from sqlalchemy import Integer, String, Table, Column, MetaData

# Load environment variables from .env file
load_dotenv()

# MockOperation for connection test
class MockOperationalError(OperationalError):
    def __init__(self, message, orig=None, params=None):
        super().__init__(message, orig, params)
        self.orig = orig
        self.params = params

    def __str__(self):
        return f"MockOperationalError: {self.message}"

@pytest.fixture(scope="module")
def storage():
    """
    Test fixture for the Storage class.

    Returns:
        Storage: An instance of the Storage class.

    Raises:
        AssertionError: If the table deletion query fails.
    """
    # Get database credentials from environment variables
    host = os.getenv("TEST_HOST", "localhost")
    port = os.getenv("TEST_DB_PORT", "3306")
    database = os.getenv("TEST_DB_NAME", "test_db")
    username = os.getenv("TEST_USER", "test_user")
    password = os.getenv("TEST_USER_PASSWORD", "test_password")

    logging.info(f'{username}: {password}')
    # Connect to the storage
    storage = Storage(
        host=host, port=port, database=database, username=username, password=password
    )
    storage.connect()
    storage.execute_query("CREATE TABLE users(email VARCHAR(160));")

    yield storage

    # Delete the table after all tests have been carried out
    delete_query = "DROP TABLE users"

    assert type(storage.execute_query(delete_query)) == int
    # Disconnect from the storage
    storage.disconnect()


# ----------------- CONNECTION HANDLING TESTS -----------------


def test_successful_connection(storage):
    """
    Test Case 1.1: Successful Connection
    Description: Test if the storage model can establish a connection to the database with valid credentials.
    Expected Outcome: Connection is successfully established.
    """
    assert storage.connect() == True


def test_failed_connection_with_invalid_credentials(storage):
    """
    Test Case 1.2: Failed Connection with Invalid Credentials
    Description: Test if the storage model correctly handles failed connection attempts with invalid credentials (e.g., wrong password).
    Expected Outcome: An appropriate error is raised indicating failure to connect.
    """
    with pytest.raises(Exception):
        storage.connect()


def test_connection_timeout():
    """
    Test Case 1.3: Connection Timeout
    Description: Test how the storage model handles connection timeouts.
    Expected Outcome: A timeout error is raised after the specified timeout period.
    """
    mock_error = MockOperationalError("Connection timed out", None, None)

    with patch('models.engine.storage.create_engine', side_effect=mock_error):
        with pytest.raises(MockOperationalError) as e:
            storage = Storage(
                    host=os.getenv("TEST_HOST", "default_host"),
                    username=os.getenv("TEST_USER", "default_user"),
                    database=os.getenv("TEST_DB_NAME", "default_database"),
                    password=os.getenv("TEST_USER_PASSWORD", "default_password"),
                    port=int(os.getenv("TEST_DB_PORT", 3306)),
                    timeout=5
                    )


def test_disconnecting_from_database(storage, mocker):
    """
    Test Case 1.4: Disconnecting from Database
    Description: Test if the storage model can properly disconnect from the database.
    Expected Outcome: Connection is successfully closed without errors.
    """
    storage.connect()

    mock_commit = mocker.patch.object(storage._session, 'commit')
    mock_rollback = mocker.patch.object(storage._session, 'rollback')
    mock_close = mocker.patch.object(storage._session, 'close')

    storage._session.is_actie = True

    storage.disconnect()

    mock_commit.assert_called_once()
    mock_close.assert_called_once()
    mock_rollback.assert_not_called()


# ----------------- CRUD OPERATION TESTS -----------------


# expected to fail
def test_inserting_data(storage):
    """
    Test Case 2.1: Inserting Data
    Description: Test inserting valid data into a table.
    Expected Outcome: Data is inserted, and the correct ID is returned.
    """
    data = {"name": "John Doe", "age": 30, "email": "johndoe@example.com"}
    inserted_id = storage.insert("users", data)
    assert isinstance(inserted_id, int)


# expected to fail
def test_inserting_data_with_missing_fields(storage):
    """
    Test Case 2.2: Inserting Data with Missing Fields
    Description: Test inserting data with missing non-nullable fields.
    Expected Outcome: An error is raised indicating that a required field is missing.
    """
    data = {"name": "John Doe", "age": 30}
    with pytest.raises(Exception):
        storage.insert("users", data)


def test_inserting_duplicate_unique_fields(storage):
    """
    Test Case 2.3: Inserting Duplicate Unique Fields
    Description: Test inserting data that violates a unique constraint (e.g., duplicate username).
    Expected Outcome: A unique constraint violation error is raised.
    """
    data = {"username": "johndoe", "email": "johndoe@example.com"}
    with pytest.raises(Exception):
        storage.insert("users", data)


def test_updating_data(storage):
    """
    Test Case 2.4: Updating Data
    Description: Test updating existing data in a table.
    Expected Outcome: Data is updated successfully, and the number of affected rows is returned.
    """
    data = {"name": "John Doe", "age": 31, "email": "johndoe@example.com"}
    condition = "id = 1"
    affected_rows = storage.update("users", data, condition)
    assert affected_rows == 1


def test_updating_non_existent_record(storage):
    """
    Test Case 2.5: Updating Non-Existent Record
    Description: Test updating a record that does not exist.
    Expected Outcome: No rows are affected, and an appropriate response is returned.
    """
    data = {"name": "John Doe", "age": 31, "email": "johndoe@example.com"}
    condition = "id = 100"
    affected_rows = storage.update("users", data, condition)
    assert affected_rows == 0


def test_deleting_data(storage):
    """
    Test Case 2.6: Deleting Data
    Description: Test deleting data from a table.
    Expected Outcome: Data is deleted successfully, and the number of affected rows is returned.
    """
    condition = "id = 1"
    affected_rows = storage.delete("users", condition)
    assert affected_rows == 1


def test_deleting_non_existent_record(storage):
    """
    Test Case 2.7: Deleting Non-Existent Record
    Description: Test deleting a record that does not exist.
    Expected Outcome: No rows are affected, and an appropriate response is returned.
    """
    condition = "id = 100"
    affected_rows = storage.delete("users", condition)
    assert affected_rows == 0


def test_fetching_single_record(storage):
    """
    Test Case 2.8: Fetching Single Record
    Description: Test fetching a single record using a valid query.
    Expected Outcome: The correct record is returned.
    """
    query = "SELECT * FROM users WHERE id = 1"
    record = storage.fetch_one(query)
    assert record["id"] == 1


def test_fetching_all_records(storage):
    """
    Test Case 2.9: Fetching All Records
    Description: Test fetching all records from a table.
    Expected Outcome: All records are returned in a list.
    """
    query = "SELECT * FROM users"
    records = storage.fetch_all(query)
    assert len(records) > 0


def test_fetching_with_complex_queries(storage):
    """
    Test Case 2.10: Fetching with Complex Queries
    Description: This test case verifies the functionality of fetching data using complex SQL queries, such as joins and subqueries.
    Expected Outcome: The data is fetched correctly and returned as expected.
    """
    query = "SELECT u.*, p.* FROM users u JOIN profiles p ON u.id = p.user_id WHERE u.age > 30"
    records = storage.fetch_all(query)
    assert len(records) > 0


# ----------------- DATA SECURITY TESTS -----------------
def test_encrypting_sensitive_data(storage):
    """
    Test Case 6.1: Encrypting Sensitive Data
    Description: Test storing and retrieving encrypted data (e.g., passwords).
    Expected Outcome: Sensitive data is encrypted before storage and decrypted correctly when retrieved.
    """
    password = "password123"
    encrypted_password = storage.encrypt_data(password)
    decrypted_password = storage.decrypt_data(encrypted_password)
    assert decrypted_password == password


# def test_auditing_changes(storage):
#     """
#     Test Case 6.3: Auditing Changes
#     Description: Test logging of changes made to roles, permissions, and sensitive data.
#     Expected Outcome: All changes are correctly logged for auditing purposes.
#     """
#     # Test role changes
#     user_id = 1
#     roles_before = storage.get_user_roles(user_id)
#     storage.assign_roles(user_id, ["admin"])
#     roles_after = storage.get_user_roles(user_id)
#     assert roles_before != roles_after

#     # Test permission changes
#     user_id = 1
#     permissions_before = storage.get_user_permissions(user_id)
#     storage.assign_permissions(user_id, ["create", "delete"])
#     permissions_after = storage.get_user_permissions(user_id)
#     assert permissions_before != permissions_after

#     # Test sensitive data changes
#     user_id = 1
#     sensitive_data_before = storage.get_sensitive_data(user_id)
#     storage.update_sensitive_data(user_id, {"password": "new_password"})
#     sensitive_data_after = storage.get_sensitive_data(user_id)
#     assert sensitive_data_before != sensitive_data_after
