#!/usr/bin/env python3
import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """Decorator to log SQL queries with timestamp before execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = args[0] if args else kwargs.get('query', '')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Executing query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Example usage
if __name__ == "__main__":
    users = fetch_all_users(query="SELECT * FROM users")
    print("Fetched users:", users)