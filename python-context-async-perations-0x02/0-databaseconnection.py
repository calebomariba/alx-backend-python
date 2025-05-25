#!/usr/bin/env python3
import sqlite3

class DatabaseConnection:
    """Context manager for handling SQLite database connections."""
    def __init__(self, db_name="users.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Open connection and return cursor."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def __exit__(self, exc_type, exc_value, traceback):
        """Commit changes, close cursor and connection."""
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
    try:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
            for row in results:
                print(row)
    except sqlite3.Error as e:
        print(f"Query error: {e}")