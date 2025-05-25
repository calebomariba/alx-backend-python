#!/usr/bin/env python3
import sqlite3
import requests
import csv
import io

def create_users_table(conn):
    """Create the users table if it doesn't exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- AUTO-INCREMENT
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,                -- Optional: to prevent duplicates
            age INTEGER NOT NULL
        );
    """)
    conn.commit()
    cursor.close()

def load_csv_to_sqlite(csv_url, db_name="users.db"):
    """Download CSV from URL and load into SQLite database."""
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
        csv_content = response.text

        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        create_users_table(conn)

        csv_file = io.StringIO(csv_content)
        csv_reader = csv.DictReader(csv_file)

        expected_headers = {'name', 'email', 'age'}
        if not expected_headers.issubset(csv_reader.fieldnames):
            print(f"Error: CSV missing required headers. Found: {csv_reader.fieldnames}")
            return

        for row in csv_reader:
            if not all([row.get('name'), row.get('email'), row.get('age')]):
                print(f"Skipping row with missing data: {row}")
                continue
            try:
                age = int(row['age'])
                cursor.execute("""
                    INSERT INTO users (name, email, age)
                    VALUES (?, ?, ?);
                """, (row['name'], row['email'], age))
            except ValueError:
                print(f"Invalid age value: {row['age']}, skipping row")
                continue
            except sqlite3.IntegrityError:
                print(f"Duplicate or invalid data for email: {row['email']}, skipping")
                continue

        conn.commit()
        print("Data loaded successfully")
    except requests.RequestException as e:
        print(f"Error downloading CSV: {e}")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    csv_url = "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIARDDGGGOUSBVO6H7D%2F20250525%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250525T100227Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=9d252101fb4f78eb62b0c2700eb44633edef9a8f7a99425bffdb4cf357d30b92"
    load_csv_to_sqlite(csv_url)
