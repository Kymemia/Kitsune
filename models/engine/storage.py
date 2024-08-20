#!/usr/bin/env python3

"""
This is the storage model for Kitsune,
containing every model and attribute and method
that will be used for the site
"""
from sqlalchemy import create_engine, Table, MetaData, Update, Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Union, Tuple, Dict
import mysql.connector
from mysql.connector import Error

# Database url + creation of SQLAlchemy engine + Configured session class + creation of session instance


class Storage:
    """
    class definition that contains
    all the models and attributes
    that will be used by the user.
    """
    def __init__(
            self, host: str, user: str,
            password: str, database: str,
            port=3306, drivername:str = 'mysql+pymysql'
            ) -> None:
        """
        method definition to initialize all the attributes
        of the class as listed below:

        Args:
        host => This is the the IP address of the MySQL server.
        user => This is the username for authenticating the database.
        password => This will be used to authenticate
                        the specific MySQL database.
        database => This is the database's specific name.
        port => This is the port number where MySQL server is listening.
                It is set to the default port.
        Example
        ---------
        """
        db_config = {
                'drivername': driver,
                'username': user,
                'password': password,
                'host': host,
                'port': port,
                'database': database
                }

        self._uri = URL.create(**db_config)
        self._engine = create_engine(self._uri)
        self._SessionFactory = sessionmaker(bind=self._engine)
        self._session = self._SessionFactory

    def connect(self) -> None:
        """
        This is the method definition to try and establish
        a connection to the MySQL server using the following parameters:
        host => This is the the IP address of the MySQL server.
        user => This is the username for authenticating the database.
        password => This will be used to authenticate
                    the specific MySQL database.
        database => This is the database's specific name.
        port => This is the port number where MySQL server is listening.
                    It is set to the default port.

        If successful, a cursor object should be created from the connection.
        Else, returns the error caught during the connection process.
        """
        try:
            self._engine = create_engine(self._uri)

            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            self._session = SessionLocal()

            print("Success! SQLAlchemy connected.")
        except SQLAlchemyError as e:
            print(f"Error connecting to the database: {e}")
            self._session.rollback()
            raise

    def disconnect(self) -> None:
        """
        This be a method definition to disconnect the connection to SQLAlchemy.
        It also checks if the connection exists, then closes it.
        """
        if self._session:
            try:
                if self._session.is_active:
                    self._session.commit()
                print("Pending transactions committed")
            except Exception as e:
                self._session.rollback()
                print(f"Error occured >> {e}. Transactions rolled back.")
            finally:
                self._session.close()
                print("SQLAlchemy connection closed")

    def execute_query(self, query: str, params: Tuple[str] = None) -> int:
        """
        This method definition executes an SQL using SQLAlchemy's interface

        Args:
        query => this is the SQL query that'll be executed
        params => this is a tuple of parameters that'll be used
                    in the SQL query (E.g: username/email)

        Returns:
            int: The number of rows affected by the error on success.
        Raises:
            Exception: Returns the caught error.

        Example:
            To update a user's email in our database:

            query = "UPDATE users SET email = :email
                    WHERE username = :username"
        """
        try:
            query_statement = text(query)
            result = self._session.execute(query_statement, params)
            self._session.commit()
            return result.rowcount
        except SQLAlchemyError:
            print("Error executing error: {e}")
            self._session.rollback()
            raise

    def fetch_one(
            self, query: str,
            params: Tuple[str] = None
            ) -> Union[Dict, Tuple]:
        """
        This method definition executes an SQL query using SQLAlchemy
        and fetches only a single record from a certain result set.
        (E.g.: primary key or unique user_id)

        Args:
        query => This is the SQL query that will be executed (str).
        params => This is a tuple of parameters
                    that'll be used in the SQL query
                        (Tuple[str], optional).

        Returns:
            A single record from the result set,
            either in dict or tuple, on success.
        
        Raises:
            SQLAlchemyError caught during execution.
            
        Example:
            query = "SELECT * FROM users WHERE username = :username"
        """
        try:
            query_statement = text(query)
            result = self._session.execute(query_statement, params)
            record = result.fetchone()
            self._session.commit()
            return record
        except SQLAlchemyError as e:
            print(f"Error fetching record: {e}")
            self._session.rollback()
            raise

    def fetch_all(
            self, query: str,
            params: Tuple[str] = None
            ) -> List[Union[Dict, Tuple]]:
        """
        This method definition executes a SQL query using SQLAlchemy
        and fetches all the records from the result set.
            (E.g: Fetching all users from the Users table)

        Args:
            query => This is the SQL query to be executed.
            params => This is a tuple of parameters
                        to be used in the SQL query.

        Returns:
            List[Union[Dict, Tuple]]: A list of records
                                    from the result set on success.
        Raise:
            SQLAlchemy error caught during query execution.

        Example:
            query = "SELECT * FROM users WHERE status = :status"
        """
        try:
            query_statement = text(query)
            result = self._session.execute(query_statement, params)
            records = result.fetchall()
            self._session.commit()
            return records
        except SQLAlchemyError as e:
            print(f"Error fetching records: {e}")
            self._session.rollback()
            raise

    def insert(self, table: str, data: Dict[str, any]) -> int:
        """
        This method definition inserts new data
        into a specified table based on the provided data.

        Args:
            table(str) => This is the name of the table
                        where the record will be inserted.
            data (Dict[str, any]) => This is a dictionary where keys == column names
                        and values are the corresponding values
                            that will be inserted.

        Returns:
            int: The Id of the inserted data on success.

        Raises:
            SQLAlchemy error if there was an error durinf execution.

        Example:
            table = 'users'
            data = {'username': 'senor_mcmuffins', 'email': 'senor@mcmuffins.com'}
            inserted_id = self.insert(table, data)
        """
        try:
            metadata = MetaData(bind=self._engine)
            target_table = Table(table, metadata, autoload_with=self._engine)
            query_statement = target_table.insert().values(data)
            result = self._session.execute(query_statement)
            self._session.commit()
            return result.inserted_primary_key[0] if result.inserted_primary_key else None
        except SQLAlchemyError as e:
            print(f"Error inserting data: {e}")
            self._session.rollback()
            raise

    def update(self, table: str, data: Dict[str, any], condition: str) -> int:
        """
        This method definition updates records
        of a specified table based on the provided data
        and custom conditions specified by the user.

        Args:
            table (str) => This is the name of the table that'll be updated.
            data (Dict[str, any]) => This is a dictionary where keys == column names
                    and values  == new values to be set.
            condition (str) => This is the condition to narrow down
                        which records will be updated.

        Returns:
            (int): The number of rows affected by the update on success.
        Raises:
            SQLAlchemyError: Should an error occur while executing the query.

        Example:
            *While using a parameterized condition with a dictionary*
            rows_updated = self.update('users', {'email': 'senor@mcmuffins.com'}, {'username': 'senor_mcmuffins'})

            *While using an SQL condition*
            rows_updated = self.update('users', {'email': 'senor@mcmuffins.com'}, 'username = :username')
        """
        try:
            metadata = MetaData(bind=self._engine)
            target_table = Table(table, metadata, autoload_with=self._engine)
            if isinstance(condition, str):
                query_statement = update(target_table).values(data).where(text(condition))
            elif isinstance(condition, dict):
                condition_expr = [
                        target_table.c[key] == value for key, value in condition.items()
                        ]
                query_statement = update(target_table).values(data).where(*condition_expr)
            else:
                raise ValueError("The condition must be a string or a dictionary")

            result = self._session.execute(query_statement)
            self._session.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            print(f"Error updating records: {e}")
            self._session._rollback()
            raise

    def delete(self, table: str, condition: str) -> int:
        """
        This method definition deletes items from a specified table
        based on a user's custom condition.

        Args:
            table (str) => This is the table name
                from which items will be deleted.
            condition (Union[str, dict]) => This is the condition
                to specify which items to delete.

        Returns:
            int: The number of rows affected on success.
        
        Raise:
            SQLAlchemyError should an error during the deletion operation.

        Example:
            rows_deleted = self.delete('users', {'username': 'senor_mcmuffins'})
        """
        try:
            metadata = MetaData(bind=self._engine)
            target_table = Table(table, metadata, autoload_with=self._engine)

            if isinstance(condition, str):
                query_statement = delete(target_table).where(text(condition))
            elif isinstance(condition, dict):
                condition_expr = [
                        target_table.c[key] == value for key, value in condition.items()
                        ]
                query_statement = delete(target_table).where(*condition_expr)
            else:
                raise ValueError("Condition must be a string or a dictionary")

            result = self._session.execute(query_statement)
            self._session.commit()
            return self._cursor.rowcount
        except SQLAlchemyError as e:
            print(f"Error deleting data: {e}")
            self._session.rollback()
            raise

    def begin_transaction(self) -> None:
        """
        This method definition starts a new database transaction.
        It ensures all operations after this transaction has started
        is treated as a one unit of work, no matter the number
        of operations carried out.
        Very helpful to maintain data integrity.
            *Provides ACID benefits*

        Raises:
            SQLAlchemyError should an error arise when starting the transaction.
        """
        try:
            self._session.begin()
            print("Transaction started")
        except SQLAlchemyError as e:
            print(f"Error starting transaction: {e}")
            raise

    def commit_transaction(self) -> None:
        """
        This method definition commits the database transaction
        that one is working on, thus making all changes permanent
        to the database.

        Raises:
            SQLAlchemyError should an error occur while committing the transaction.
        """
        try:
            self._session.commit()
            print("Transaction committed successfully")
        except SQLAlchemyError as e:
            print(f"Error committing transaction: {e}")
            self._session.rollback()
            raise

    def rollback_transaction(self) -> None:
        """
        This method definition allows one to revert/undo
        the current transaction should an error occur,
        thus undoing all changes made
        during the transaction.

        Raises:
            SQLAlchemy error should rollback turn out to be unsuccessful.
        """
        try:
            self._session.rollback()
            print("Transaction rolled back successfully")
        except SQLAlchemyError as e:
            print(f"Error rolling back transaction: {e}")
            raise

    def create_table(self, table_name: str, columns: dict) -> dict:
        """
        This method definition allows a user to create a new table
        with a specific name and a specific number
        of columns using SQLAlchemy's table definition.

        Args:
            table_name => This is the name that'll be assigned
                            to the table created.
            columns => This will be the number of columns assigne
                        to the table based on the user's needs.

        Returns:
            Created table on success.
        
        Raises:
            SQLAlchemyError should an error occur while creating the table.
        """
        metadata = MetaData()

        table = Table(
                table_name,
                metadata,
                *[
                    Column(column_name, column_type)
                    for column_name, column_type in columns.items()
                    ]
                )
        try:
            table.create(self._engine)
            print(f"Table '{table_name} created successfully'")
        except SQLAlchemyError as e:
            print(f"Error creating table: {e}")
            raise

    def drop_table(self, table_name: str) -> None:
        """
        This method definition allows a user to delete a table
        by specifying its name.
        If the table_name exists in the database, the process is a success.
        After doing so, the transaction is committed
        to make it permanent.

        Args:
        table_name => This will be the name
                        of the table to be used for this operation.

        Should an error occur, it's caught and printed,
        and the transaction is rolled back
        to undo the changes that might have caused it.
        """
        query = f"DROP TABLE IF EXISTS {table_name}"
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Error as e:
            print(f"Error dropping table: {e}")
            self.rollback_transaction()
            raise
