#!/usr/bin/env python3
seed = __import__('seed')

# Connect to MySQL server and create database
connection = seed.connect_db()
if connection:
    seed.create_database(connection)
    connection.close()
    print("connection successful")

    # Connect to ALX_prodev database
    connection = seed.connect_to_prodev()
    if connection:
        # Create table and insert data
        seed.create_table(connection)
        seed.insert_data(connection, 'user_data.csv')

        # Verify database and table
        cursor = connection.cursor()
        cursor.execute("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'ALX_prodev';")
        if cursor.fetchone():
            print("Database ALX_prodev is present")
        cursor.execute("SELECT * FROM user_data LIMIT 5;")
        rows = cursor.fetchall()
        print("First 5 rows:", rows)
        cursor.close()

        # Test generator
        print("Streaming first 5 rows from user_data:")
        count = 0
        for row in seed.stream_user_data(connection):
            print(row)
            count += 1
            if count >= 5:
                break

        connection.close()