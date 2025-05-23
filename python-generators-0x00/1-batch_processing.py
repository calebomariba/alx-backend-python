#!/usr/bin/env python3
import mysql.connector
import os


def stream_users_in_batches(batch_size):
    """Yields batches of users from the user_data table."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            database="ALX_prodev"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data;")
        
        batch = []
        for row in cursor:
            user = {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            batch.append(user)
            if len(batch) == batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        try:
            if connection.is_connected():
                connection.close()
        except Exception:
            pass


def batch_processing(batch_size):
    """Processes users in batches, printing only those over age 25."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
