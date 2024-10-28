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

class MySQLStorage:
    def __init__(self, host, user, password, database, port=3306):
        """
        method definition to initialize all the attributes
        of the class as listed below

        **PARAMETERS**
        host => This is the the IP address of the MySQL server
        user => This is the username for authenticating the database
        password => This will be used to authenticate the specific MySQL database
        database => This is the database's specific name
        port => This is the port number where MySQL server is listening. It is set to the default port
        """
        self._host = host
        self._user = user
        self._password = password
        self._database = database
        self._port = port
        self._connection = None
        self._cursor = None

    def connect(self):
        """
        This is the method definition to try and establish
        a connection to the MySQL server using the following parameters:
        host => This is the the IP address of the MySQL server.
        user => This is the username for authenticating the database.
        password => This will be used to authenticate the specific MySQL database.
        database => This is the database's specific name.
        port => This is the port number where MySQL server is listening.
                    It is set to the default port.
>>>>>>> add_pycache_in_gitignore

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
            self._connection = mysql.connector.connect(
                    host=self._host,
                    user=self._user,
                    password=self._password,
                    database=self._database,
                    port=self._port
                    )
            self._cursor = self._connection.cursor(dictionary=True)
            print("Success! MySQL connected.")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def disconnect(self):
        """
        This be a method definition to disconnect the connection to MySQL.
        It checks if the cursor exists and is open, then closes it.
        It also checks if the connection exists and is open,
        then closes it as well.
        """
        if self._cursor:
            self._cursor.close()
        if self._connection:
            self._connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None):
        """
        This method definition executes an SQL query based
        on the query given by the user and parameters

        **PARAMETERS**
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

    # TODO change to fetch k where default is 1 if you want to fetch x number of elements
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
            record = result.scalar()
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
                if isinstance(table, str):
                    metadata = Metadata()
                    target_table = Table(table, metadata, autoload_with=self._engine)
                    self._session.execute(target_table.insert(), data)
                else:
                    self._session.bulk_insert_mappings(table, data)
                self._session.commit()
                return [record['uid'] for record in data] # Have discussion about what to set as primary key
            else:
                if isinstance(table, str):
                    metadata = MetaData()
                    target_table = Table(table, metadata, autoload_with=self._engine)
                    query_statement = target_table.insert().values(data)
                    result = self._session.execute(query_statement)
                else:
                    obj = table(**data)
                    self._session.add(obj)
                    self._session.commit()
                    return obj.uid

                self._session.commit()
                return result.inserted_primary_key if result.inserted_primary_key else None

        except SQLAlchemyError as e:
            logging.info(f"Error inserting data: {e}")
            self._session.rollback()
            raise

    def update(self, model_instance) -> int:
        """
        method definition that updates an existing SQLAlchemy object in the DB

        Args:
            model_instance: This is the instance
                    of the SQLAlchemy model to be updated

        Returns:
            int: The number of rows affected by the updated
            (1 if successful, assuming 1 row was worked on)
        """
        try:
            self._session.merge(model_instance)
            self._session.commit()
            return 1
        except SQLAlchemyError as e:
            logging.info(f"Error updating record: {e}")
            self._session.rollback()
            raise

    def delete(self, model_instance) -> int:
        """
        method definition that deletes an existing SQLAlchemy object (record) from the DB

        Args:
            model_instance: this is an instance
                of the SQLAlchemy model to be deleted

        Returns:
            int: the number of rows to be affected

        Raises:
            SQLAlchemyError: Should an error occur during deletion
        """
        try:
            self._session.delete(model_instance)
            self._session.commit()
            return 1
        except SQLAlchemyError as e:
            logging.info(f"Error deleting record: {e}")
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
        Returns the number of rows affected by the error on success.
        Else, returns the caught error.
        """
        try:
            self._cursor.execute(query, params)
            self._connection.commit()
            return self._cursor.rowcount
        except Error as e:
            print("Error executing error: {e}")
            self.rollback_transaction()
            raise

    def fetch_one(self, query, params=None):
        """
        This method definition executes a SQL query and fetches
        only a single record from a certain result set.
        (E.g.: primary key or unique user_id)

        **PARAMETERS**
        query => This is the SQL query that will be executed (string).
        params => This is a tuple of parameters
                    that'll be used in the SQL query.

        Returns a single record from the result set, either in dict or tuple, on success.
        Else, returns error caught.
        """
        try:
            self._cursor.execute(query, params)
            return self._cursor.fetchone()
        except Error as e:
            print(f"Error fetching record: {e}")
            raise

    def fetch_all(self, query, params=None):
        """
        This method definition executes a SQL query
        and fetches all the records from the result set.
            (E.g: Fetching all users from the Users table)

        **PARAMETERS**
        query => This is the SQL query to be executed.
        params => This is a tuple of parameters
                    to be used in the SQL query.

        Returns a list of records from the result set on success.
        Else, returns error caught.
        """
        try:
            self._cursor.execute(query, params)
            return self._cursor.fetchall()
        except Error as e:
            print(f"Error fetching records: {e}")
            raise

    def insert(self, table, data):
        """
        This method definition inserts new data
        into a specified table based on the provided data.
        It creates a string of placeholders for the SQL query based
        on the number of data items then creates
        a string of column names for the query itself.

        **PARAMETERS**
        table => This is the name of the table
                    where the record will be inserted.
        data => This is a dictionary where keys == column names
                    and values are the corresponding values
                        that will be inserted.

        Returns the Id of the inserted data on success.
        Else, returns caught error.
        """
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        try:
            self._cursor.execute(query, list(data.values()))
            self._connection.commit()
            return self._cursor.lastrowid
        except Error as e:
            print(f"Error inserting data: {e}")
            raise

    def update(self, table, data, condition):
        """
        This method definition updates records
        of a specified table based on the provided data
        and custom conditions specified by the user.
        
        **PARAMETERS**
        table => This is the name of the table that'll be updated.
        data => This is a dictionary where keys == column names
                    and values  == new values to be set.
        condition => This is the condition to narrow down
                        which records will be updated.

        Returns the number of rows affected by the update on success.
        Else, returns caught error.
        """
        set_clause =", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        try:
            self._cursor.execute(query, list(data.values()))
            self._connection.commit()
            return self._cursor.rowcount
        except Error as e:
            print(f"Error updating: {e}")
            raise

    def delete(self, table, condition):
        """
        This method definition deletes items from a specified table
        based on a user's custom condition.

        **PARAMETERS**
        table => This is the table name from which items will be deleted.
        condition => This is the condition to specify which items to delete.

        Returns number of rows affected on success.
        Else, returns caught error.
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        try:
            self._cursor.execute(query)
            self._connection.commit()
            return self._cursor.rowcount
        except Error as e:
            print(f"Error deleting data: {e}")
            self.rollback_transaction()
            raise

    def begin_transaction(self):
        """
        This method definition starts a new database transaction.
        It ensures all operations after this transaction has started
        is treated as a one unit of work, no matter the number
        of operations carried out.
        Very helpful to maintain data integrity.
            *Provides ACID benefits*
        """
        self._connection.start_transaction()

    def commit_transaction(self):
        """
        This method definition commits the database transaction
        that one is working on, thus making all changes permanent
        to the database.

        Returns specific caught error in the event of an error.
        """
        try:
            self._connection.commit()
        except Error as e:
            print(f"Error committing transaction: {e}")
            raise

    def rollback_transaction(self):
        """
        This method definition allows one to revert/undo
        the current transaction should an error occur,
        thus undoing all changes made
        during the transaction.

        Returns any error/exception that might happen if unsuccessful.
        """
        try:
            self._connection.rollback()
        except Error as e:
            print(f"Error rolling back transaction: {e}")
            raise

    def create_table(self, table_name, columns):
        """
        This method definition allows a user to create a new table
        with a specific name and a specific number of columns.
        Once the table is created with a query,
        the transaction is committed to make the creation permanent.

        **PARAMETERS**
        table_name => This is the name that'll be assigned
                        to the table created.
        columns => This will be the number of columns assigned
                    to the table based on the user's needs.

        Returns created table on success.
        Else, the transaction is rolled back to undo
        the changes that might have caused the caught error.
        """
        columns_with_types = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE {table_name} ({columns_with_types})"
        try:
            self._cursor.execute(query)
            self._connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")
            self.rollback_transaction()
            raise

    def drop_table(self, table_name):
        """
        This method definition allows a user to delete a table
        by specifying its name.
        If the table_name exists in the database, the process is a success.
        After doing so, the transaction is committed
        to make it permanent.

        **PARAMETERS**
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
