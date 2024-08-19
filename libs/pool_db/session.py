from threading import Lock
from typing import List, Optional, Tuple

import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor


class PoolDBSession:
    """
    A class to manage PostgreSQL database sessions using connection pooling.

    Attributes:
        conn_params (dict): Database connection parameters.
        print_lock (Lock): A lock to manage print statements from multiple threads.
        connection (connection): The database connection object.
        cursor (cursor): The cursor object for executing queries.
        db_pool (SimpleConnectionPool): The connection pool for managing connections.
    """

    def __init__(self, db_config: dict):
        """
        Initialize the DBSession with the provided database configuration.

        Args:
            db_config (dict): The database connection configuration.

        Raises:
            ValueError: If the database configuration is missing.
        """
        if not db_config:
            raise ValueError("Missing database configuration")

        self.conn_params = db_config
        self.print_lock = Lock()
        self.connection = None
        self.cursor = None
        self.db_pool = None

    def __enter__(self):
        """
        Enter the runtime context related to this object. Establish a connection and create a cursor.

        Returns:
            DBSession: The instance itself.
        """
        self.db_pool = pool.SimpleConnectionPool(**self.conn_params)
        self.connection = self.db_pool.getconn()
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()

        self.cursor.close()
        self.connection.close()
        self.db_pool.putconn(self.connection)

    def execute_query(self, query, params: Optional[Tuple] = None):
        """
        Execute a SQL query with optional parameters.

        Args:
            query (str or sql.SQL): The SQL query to execute.
            params (tuple, optional): The parameters for the SQL query.

        Returns:
            psycopg2.extensions.cursor: The cursor object after executing the query.

        Raises:
            psycopg2.Error: If an error occurs during query execution.
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor
        except psycopg2.Error as ex:
            self.connection.rollback()
            with self.print_lock:
                print(f"Error executing query: {ex}")
            raise

    @staticmethod
    def __generate_columns(columns: Optional[List[str]] = None) -> sql.SQL:
        """
        Generate a SQL string for the columns to be selected.

        Args:
            columns (List[str], optional): The list of column names.

        Returns:
            sql.SQL: The SQL representation of the columns.
        """
        if columns:
            return sql.SQL(", ").join(map(sql.Identifier, columns))
        else:
            return sql.SQL("*")

    @staticmethod
    def __generate_conditions(conditions: dict) -> Tuple[sql.SQL, Tuple]:
        """
        Generate the SQL string and parameters for the WHERE clause.

        Args:
            conditions (dict): The conditions for the WHERE clause.

        Returns:
            tuple: A tuple containing the SQL string and the parameters.
        """
        condition_statements = [
            sql.SQL("{} = %s").format(sql.Identifier(key)) for key in conditions
        ]
        condition_string = sql.SQL(" AND ").join(condition_statements)
        params = tuple(conditions.values())
        return condition_string, params

    def get_one_where(
        self, table: str, columns: List[str] = None, conditions: dict = None
    ):
        """
        Fetch a single row from the table that matches the conditions.

        Args:
            table (str): The table name.
            columns (List[str], optional): The list of columns to select.
            conditions (Dict[str, Union[str, int]], optional): The conditions for the WHERE clause.

        Returns:
            dict or None: The fetched row as a dictionary, or None if no row is found.
        """
        column_string = self.__generate_columns(columns=columns)
        cond_string, params = self.__generate_conditions(conditions)

        query = sql.SQL("SELECT {cols} FROM {tname} WHERE {cond} LIMIT 1;").format(
            cols=column_string, tname=sql.Identifier(table), cond=cond_string
        )
        result = self.execute_query(query, params).fetchone()

        return result or None

    def get_all(self, table: str, columns: List[str] = None):
        """
        Fetch all rows from the table.

        Args:
            table (str): The table name.
            columns (List[str], optional): The list of columns to select.

        Returns:
            list: A list of dictionaries representing the rows.
        """

        query = sql.SQL("SELECT * FROM {tname};").format(tname=sql.Identifier(table))
        return self.execute_query(query).fetchall()

    def select(self, table: str, columns: List[str] = None, conditions: dict = None):
        """
        Fetch all rows from the table that match the conditions.

        Args:
            table (str): The table name.
            columns (List[str], optional): The list of columns to select.
            conditions (Dict[str, Union[str, int]], optional): The conditions for the WHERE clause.

        Returns:
            list or None: A list of dictionaries representing the rows, or None if no rows are found.
        """
        column_string = self.__generate_columns(columns=columns)
        cond_string, params = self.__generate_conditions(conditions)

        query = sql.SQL("SELECT {cols} FROM {tname} WHERE {cond};").format(
            cols=column_string, tname=sql.Identifier(table), cond=cond_string
        )
        result = self.execute_query(query, params).fetchall()

        return result or None

    def insert(self, table: str, **kwargs):
        columns = kwargs.keys()
        values = kwargs.values()

        query = sql.SQL("INSERT INTO {table} ({cols}) VALUES ({vals})").format(
            table=sql.Identifier(table),
            cols=sql.SQL(", ").join(map(sql.Identifier, columns)),
            vals=sql.SQL(", ").join([sql.Placeholder()] * len(values)),
        )

        return self.execute_query(query, tuple(values))

    @staticmethod
    def sanitize_input(value):
        """
        Sanitize the input to prevent SQL injection.

        Args:
            value (str or any): The input value.

        Returns:
            str or any: The sanitized input value.
        """
        return value.replace("'", "''") if isinstance(value, str) else value
