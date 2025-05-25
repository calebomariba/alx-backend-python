#!/usr/bin/env python3
import sqlite3
import functools

def with_db_connection(func):
    """Decorator to handle opening and closing SQLite database connections."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = sqlite3.connect('users.db')
            result = func(conn, *args, **kwargs)
            conn.commit()  # Commit changes (though managed by transactional)
            return result
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    return wrapper

def transactional(func):
    """Decorator to manage database transactions with commit or rollback."""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
            return result
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed, rolled back: {e}")
            raise  # Re-raise for debugging
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE user_id = ?", (new_email, user_id))
    return cursor.rowcount

# Example usage
if __name__ == "__main__":
    updated_rows = update_user_email(
        user_id= 1,
        new_email="Crawford_Cartwright@hotmail.com"
    )
    print(f"Updated {updated_rows} user(s)")