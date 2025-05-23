#!/usr/bin/env python3

import mysql.connector
import os

def stream_users_in_batches(batch_size):
    """Generator that yields users in batches of batch_size."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        database="ALX_prodev"
    )
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user_id, name, email, age FROM user_data;")
        rows = cursor.fetchall()  # fetch all results at once

        # Yield in batches
        for i in range(0, len(rows), batch_size):
            batch = [{
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            } for row in rows[i:i+batch_size]]
            yield batch

    finally:
        cursor.close()
        connection.close()


def batch_processing(batch_size):
    """Processes batches and yields users over age 25."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(user)
