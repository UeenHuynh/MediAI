"""Tools for agents to interact with database."""

import psycopg2
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Tool for database operations."""

    def __init__(self, connection_string: str):
        """
        Initialize database tool.

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        """Establish database connection."""
        if not self.conn or self.conn.closed:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Database connection established")

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of dictionaries (rows)
        """
        self.connect()
        cursor = self.conn.cursor()

        try:
            cursor.execute(query, params)

            if cursor.description:  # SELECT query
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return [dict(zip(columns, row)) for row in rows]
            else:  # INSERT/UPDATE/DELETE
                self.conn.commit()
                return []

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            cursor.close()

    def query_to_dataframe(self, query: str) -> pd.DataFrame:
        """
        Execute query and return DataFrame.

        Args:
            query: SQL query string

        Returns:
            pandas DataFrame
        """
        self.connect()
        return pd.read_sql(query, self.conn)

    def insert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        if_exists: str = 'append'
    ):
        """
        Insert DataFrame into table.

        Args:
            df: pandas DataFrame
            table_name: Target table (schema.table)
            if_exists: 'append' or 'replace'
        """
        self.connect()
        df.to_sql(
            name=table_name.split('.')[1],  # table name without schema
            schema=table_name.split('.')[0],  # schema name
            con=self.conn,
            if_exists=if_exists,
            index=False,
            method='multi'
        )
        logger.info(f"Inserted {len(df)} rows into {table_name}")

    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")
