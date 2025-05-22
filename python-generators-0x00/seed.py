#!/usr/bin/env python3
import mysql.connector
import csv
import uuid
import os

def connect_db():
    """Connects to the MySQL server."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_ROOT_PASSWORD")
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        connection.commit()
        print("Database ALX_prodev created or already exists")
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()

def connect_to_prodev():
    """Connects to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_ROOT_PASSWORD"),
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None

def create_table(connection):
    """Creates the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age INT NOT NULL,
            INDEX idx_user_id (user_id)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()

def insert_data(connection, data):
    """Inserts data from the CSV file into user_data, generating user_id."""
    try:
        cursor = connection.cursor()
        with open(data, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                user_id = str(uuid.uuid4())
                if not all([row.get('name'), row.get('email'), row.get('age')]):
                    print(f"Missing required column in row: {row}, skipping")
                    continue
                cursor.execute("SELECT email FROM user_data WHERE email = %s;", (row['email'],))
                if cursor.fetchone():
                    print(f"Email {row['email']} already exists, skipping")
                    continue
                insert_query = """
                INSERT INTO user_data (user_id, name, email, age)
                VALUES (%s, %s, %s, %s);
                """
                try:
                    values = (user_id, row['name'], row['email'], int(row['age']))
                    cursor.execute(insert_query, values)
                except ValueError:
                    print(f"Invalid age value: {row['age']}, skipping row")
                    continue
        connection.commit()
        print("Data inserted successfully")
    except mysql.connector.Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {data} not found")
    except KeyError as e:
        print(f"Missing column in CSV: {e}")
    finally:
        cursor.close()

def stream_user_data(connection):
    """Generator to stream rows from user_data one by one."""
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, name, email, age FROM user_data;")
        for row in cursor:
            yield row
        print("Finished streaming user_data")
    except mysql.connector.Error as e:
        print(f"Error streaming data: {e}")
    finally:
        # Consume any remaining results before closing
        if 'cursor' in locals() and cursor._executed:
            cursor.fetchall()  # Clear unread results
        cursor.close()