#!/usr/bin/env python3
import mysql.connector
import os

def stream_users():
    """Generator to stream user_data rows one by one as dictionaries."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            database="ALX_prodev"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data;")

        for row in cursor:
            yield {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }

    except mysql.connector.Error as e:
        print(f"Error streaming data: {e}")
    finally:
        # Only close AFTER generator is exhausted
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Exception:
            pass


# def stream_users():
#     """Generator with proper resource cleanup."""
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password=os.getenv("MYSQL_ROOT_PASSWORD"),
#         database="ALX_prodev"
#     )
#     cursor = connection.cursor()
#     try:
#         cursor.execute("SELECT user_id, name, email, age FROM user_data;")
#         for row in cursor:
#             yield {
#                 'user_id': row[0],
#                 'name': row[1],
#                 'email': row[2],
#                 'age': row[3]
#             }
#     finally:
#         cursor.close()
#         connection.close()
