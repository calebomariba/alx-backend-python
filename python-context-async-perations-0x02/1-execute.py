#!/usr/bin/env python3
import sqlite3

class ExecuteQuery:
    """Context manager to execute a parameterized query and manage connection."""
    def __init__(self, query, params):
        self.query = query
        self.params = params
        self.db_name = "users.db"
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        """Open connection, execute query, return results."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute(self.query, self.params)
            self.results = self.cursor.fetchall()
            return self.results
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """Commit or rollback, close cursor and connection."""
        try:
            if exc_type is None:
                self.conn.commit()  # Commit if no exception
            else:
                self.conn.rollback()  # Rollback on exception
        except sqlite3.Error as e:
            print(f"Error during transaction: {e}")
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()

# Example usage
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    params = (25,)
    try:
        with ExecuteQuery(query, params) as results:
            for row in results:
                print(row)
    except sqlite3.Error as e:
        print(f"Query error: {e}")