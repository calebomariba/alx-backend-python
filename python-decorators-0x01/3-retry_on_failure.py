#!/usr/bin/env python3
import sqlite3
import functools
import time

def with_db_connection(func):
    """Decorator to handle opening and closing SQLite database connections."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit changes (not needed for SELECT)
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """Decorator to retry database operations on failure."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(retries + 1):  # Include initial attempt
                try:
                    return func(*args, **kwargs)
                except sqlite3.Error as e:
                    last_error = e
                    if attempt < retries:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        print(f"All {retries} retries failed: {e}")
                        raise last_error
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Example usage
if __name__ == "__main__":
    users = fetch_users_with_retry()
    print(users)