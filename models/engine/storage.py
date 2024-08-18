#!/usr/bin/env python3

"""
This is the storage model for Kitsune,
containing every model and attribute and method
that will be used for the site
"""
import mysql.connector
from mysql.connector import Error


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

        If successful, a cursor object should be created from the connection.
        Else, returns the error caught during the connection process.
        """
        try:
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
