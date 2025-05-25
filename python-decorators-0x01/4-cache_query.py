#!/usr/bin/env python3
import time
import sqlite3
import functools

query_cache = {}

def cache_query(func):
    """Decorator that caches the results of database queries based on the query string."""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        if query in query_cache:
            print("Using cached result.")
            return query_cache[query]
        print("Executing query and caching result.")
        result = func(conn, query, *args, **kwargs)
        query_cache[query] = result
        return result
    return wrapper

def with_db_connection(func):
    """Handles database connection setup and teardown."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("users.db")
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call: executes and caches the query
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call: uses the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)
