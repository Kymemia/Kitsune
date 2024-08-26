#!/usr/bin/env python3

"""
This is the storage model for Kitsune,
containing every model and attribute and method
that will be used for the site
"""
import logging
from sqlalchemy import create_engine, Table, MetaData, Update, Column, delete
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Query, Session
from sqlalchemy.engine import URL
from sqlalchemy.sql import text, Select, and_
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from typing import List, Union, Tuple, Dict, Any, Type
import mysql.connector
from mysql.connector import Error



class Storage:
    """
    class definition that contains
    all the models and attributes
    that will be used by the user.
    """
    def __init__(
            self, host: str, username: str,
            database: str, password: str='',
            port=3306, drivername:str = 'mysql+pymysql',
            timeout: int = 5
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
                'drivername': drivername,
                'username': username,
                'password': password,
                'host': host,
                'port': port,
                'database': database
                }

        self._uri = URL.create(**db_config)
        logging.info(self._uri)

        self._engine = create_engine(
                self._uri,
                connect_args={"connect_timeout": timeout}
                )
        self._SessionFactory = sessionmaker(bind=self._engine)
        self._session = self._SessionFactory()

    def connect(self) -> bool:
        """
        This is the method definition to try and establish
        a connection to the MySQL server using the following parameters:
        host: This is the the IP address of the MySQL server.
        user: This is the username for authenticating the database.
        password: This will be used to authenticate
                    the specific MySQL database.
        database: This is the database's specific name.
        port: This is the port number where MySQL server is listening.
                    It is set to the default port.
        timeout: This is the set timeout for establishing
                    a connection, measured in seconds.

        If successful, a cursor object should be created from the connection.
        Else, returns the error caught during the connection process.
        """
        try:
            self._session = self._SessionFactory()
            logging.info("Success! SQLAlchemy connected.")
            return True
        except OperationalError as e:
            logging.error(f"OperationalError: {e}")
            if "timeout" in str(e).lower():
                raise TimeoutError("Connection timed out.")
            if self._session:
                self._session.close()
        except SQLAlchemyError as e:
            logging.error(f"SQLAlchemyError: {e}")
            if self._session:
                self._session.close()
        return False

    def disconnect(self) -> None:
        """
        This be a method definition to disconnect the connection to SQLAlchemy.
        It also checks if the connection exists, then closes it.
        """
        if not self._session:
            logging.warning("No active session to disconnect.")
            return
        
        try:
            if self._session.is_active:
                self._session.commit()
                logging.info("Pending transactions committed")
        except Exception as e:
            self._session.rollback()
            logging.info(f"Error occured >> {e}. Transactions rolled back.")
        finally:
            try:
                self._session.close()
                logging.info("SQLAlchemy connection closed")
            except Exception as e:
                logging.error(f"Error occured while closing the session.")

    def execute_query(self, query: Query, params: Tuple[str] = None) -> int:
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
            result = self._session.execute(text(query), params)
            self._session.commit()
            return result.rowcount
        except SQLAlchemyError:
            logging.info("Error executing query: {e}")
            self._session.rollback()
            raise

    def fetch_one(
            self, query: Select,
            params: Tuple[str] = None
            ) -> Union[Dict, Tuple]:
        """
        This method definition executes an SQLAlchemy query
        and fetches only a single record from a certain result set.
        (E.g.: primary key or unique user_id)

        Args:
        query (Select) => This is the SQLAlchemy object that will be executed.
        params (Tuple[str], optional) => This is a tuple of parameters
                    that'll be used in the query.

        Returns:
            Union[Dict, Tuple]: A single record from the result set,
            either in dict or tuple, on success.
        
        Raises:
            SQLAlchemyError caught during execution.
            
        Example:
            query = select(User).where(User.username == 'example_username')
            result = fetch_one(query)
        """
        try:
            result = self._session.execute(query, params)
            record = result.fetchone()
            self._session.commit()
            return record
        except SQLAlchemyError as e:
            logging.info(f"Error fetching record: {e}")
            self._session.rollback()
            raise

    def fetch_all(
            self, query: Select,
            params: Tuple[str] = None
            ) -> List[Union[Dict, Tuple]]:
        """
        This method definition executes an SQLAlchemy query
        and fetches all the records from the result set.
            (E.g: Fetching all users from the Users table)

        Args:
            query (Select): This is the SQLAlchemy object
                        that's representing the query to be executed.
            params (Tuple[str], optional): This is a tuple of parameters
                        to be used in the SQL query.

        Returns:
            List[Union[Dict, Tuple]]: A list of records
                                    from the result set on success.
        Raise:
            SQLAlchemy error caught during query execution.

        Example:
            query = select(User).where(User.status == 'active')
            results = fetch_all(query)
        """
        try:
            result = self._session.execute(query, params)
            records = result.fetchall()
            self._session.commit()
            return records
        except SQLAlchemyError as e:
            logging.info(f"Error fetching records: {e}")
            self._session.rollback()
            raise

    def insert(self, table: Union[str, Any], data: Union[Dict[str, any], List[Dict[str, Any]]]) -> Union[int, List[int]]:
        """
        This method definition inserts new data
        into a specified table based on the provided data.

        Args:
            table(str): This is the name of the table
                        where the record will be inserted.
            data (Union[Dict[str, any], List[Dict, str, Any]]):
                This is a dictionary where keys == column names
                        and values are the corresponding values
                            that will be inserted.

        Returns:
            Union[int, List[int]]: The Id of the inserted data on success, or a list of Ids in the event of multiple inserts.

        Raises:
            SQLAlchemy error if there was an error durinf execution.

        Example:
            *For single data insertion*
            table = User
            data = {'username': 'seno_mcmuffins', 'email': 'senor@mcmuffins.com'}
            inserted_id = self.insert(table, data)

            *For multiple data insertions*
            multiple_users = [
                {'username': 'user1', 'email': 'senor@mcmuffins'},
                {'username': 'user2', 'email': 'missus@mcmuffins'}
                ]
                inserted_ids = self.insert(table, multiple_users)

        """
        try:
            if isinstance(data, list):
                if isisnstance(table, str):
                    metadata = Metadata(bind=self._engine)
                    target_table = Table(table, metadata, autoload_with=self._engine)
                    self._session.execute(target_table.insert(), data)
                else:
                    self._session.bulk_insert_mappings(table, data)
                self._session.commit()
                return [record['id'] for record in data] # Have discussion about what to set as primary key
            else:
                if isinstance(table, str):
                    metadata = MetaData(bind=self._engine)
                    target_table = Table(table, metadata, autoload_with=self._engine)
                    query_statement = target_table.insert().values(data)
                    result = self._session.execute(query_statement)
                else:
                    obj = table(**data)
                    self._session.add(obj)
                    self._session.commit()
                    return obj.id

                self._session.commit()
                return result.inserted_primary_key[0] if result.inserted_primary_key else None

        except SQLAlchemyError as e:
            logging.info(f"Error inserting data: {e}")
            self._session.rollback()
            raise

    def update(self, model_class, data: Dict[str, Any], condition: Dict[str, Any] = None) -> int:
        """
        This method definition updates records
        of a specified table based on the provided data
        and custom conditions specified by the user.

        Args:
            model_class: This is the SQLAlchemy model for the table to be updated.
            data (Dict[str, any]): This is a dictionary where keys == column names
                    and values  == new values to be set.
            condition Union[str, Dict[str, Any]]: This is the condition to narrow down
                        which records will be updated.

        Returns:
            int: The number of rows affected by the update on success.
        Raises:
            SQLAlchemyError: Should an error occur while executing the query.

        Example:
            *While using a parameterized condition with a dictionary*
            rows_updated = self.update('users', {'email': 'senor@mcmuffins.com'}, {'username': 'senor_mcmuffins'})

            *While using an SQL condition*
            rows_updated = self.update('users', {'email': 'senor@mcmuffins.com'}, 'username = :username')
        """
        try:
            query = self._session.query(model_class).filter_by(**condition) if condition else self._session.query(model_class)
            rows_updated = query.update(data, synchronize_session='fetch')
            self._session.commit()
            return rows_updated
        except SQLAlchemyError as e:
            logging.info(f"Error updating records: {e}")
            self._session._rollback()
            raise

    def delete(self, table: str, condition: Union[str, Dict[str, Any]]) -> int:
        """
        This method definition deletes items from a specified table
        based on a user's custom condition using SQLAlchemy objects.

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
                query_statement = delete(target_table).where(and_(*condition_expr))
            else:
                raise ValueError("Condition must be a string or a dictionary")

            result = self._session.execute(query_statement)
            self._session.commit()
            return result.rowcount
        except SQLAlchemyError as e:
            logging.info(f"Error deleting data: {e}")
            self._session.rollback()
            raise

    def create_table(self, table_name: str, columns: Dict[str, Type]) -> Table:
        """
        This method definition allows a user to create a new table
        with a specific name and a specific number
        of columns using SQLAlchemy's table definition.

        Args:
            table_name (str): This is the name that'll be assigned
                            to the table created.
            columns (Dict[str, Type]): This is a dictionary where keys are column names
                and values are SQLAlchemy column types.

        Returns:
            Table: Created table on success.
        
        Raises:
            SQLAlchemyError: Should an error occur while creating the table.
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
            logging.info(f"Table '{table_name} created successfully'")
            return table
        except SQLAlchemyError as e:
            logging.info(f"Error creating table: {e}")
            raise

    def drop_table(self, table_name: str) -> None:
        """
        This method definition allows a user to delete a table
        by specifying its name.
        If the table_name exists in the database, the process is a success.

        Args:
            table_name (str): This will be the name
                            of the table to be used for this operation.

        Raise:
            SQLAlchemyError: Should an error occur while dropping the table.
        """
        metadata = MetaData(bind=self._engine)
        table = Table(table_name, metadata, autoload_with=self._engine)
        try:
            table.drop(self._engine)
            logging.info(f"Table '{table_name}' dropped successfully")
            self._session.commit()
        except SQLAlchemyError as e:
            logging.info(f"Error dropping table: {e}")
            self._session.rollback()
            raise
