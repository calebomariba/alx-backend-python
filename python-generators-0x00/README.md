# Python Generators for ALX Backend Project

This directory (`python-generators-0x00`) contains Python scripts for the ALX Backend project, focusing on database setup, data seeding, and row streaming using MySQL, as part of the `alx-backend-python` repository. The scripts demonstrate connecting to a MySQL server, creating a database and table, populating data from a CSV file, and streaming rows using a generator.

## Files

- **`README.md`**: This file, documenting the directory and its contents.
- **`seed.py`**: Python script to set up the `ALX_prodev` database, create the `user_data` table, insert data from `user_data.csv`, and stream rows with a generator.
- **`0-main.py`**: Test script to verify `seed.py` functionality, including database setup and generator streaming.
- **`user_data.csv`**: CSV file containing user data (user_id, name, email, age), sourced from [S3 URL](https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv).

## Overview

### seed.py
Implements functions to:
- **connect_db()**: Connects to the MySQL server.
- **create_database(connection)**: Creates the `ALX_prodev` database if it doesn't exist.
- **connect_to_prodev()**: Connects to the `ALX_prodev` database.
- **create_table(connection)**: Creates the `user_data` table with fields:
  - `user_id` (VARCHAR(36), Primary Key, indexed)
  - `name` (VARCHAR(255), NOT NULL)
  - `email` (VARCHAR(255), NOT NULL)
  - `age` (DECIMAL(5,2), NOT NULL)
- **insert_data(connection, data)**: Inserts data from `user_data.csv`, skipping duplicates.
- **stream_user_data(connection)**: Generator to stream `user_data` rows one by one.

### 0-main.py
Tests `seed.py` by:
- Connecting to MySQL and creating the `ALX_prodev` database.
- Creating the `user_data` table and inserting CSV data.
- Verifying the database and displaying the first 5 rows.
- Streaming the first 5 rows using the generator.

### user_data.csv
Contains user data with columns: `user_id` (UUID), `name`, `email`, `age`. Sourced from an AWS S3 bucket.

## Repository Structure

- **Repository**: `alx-backend-python`
- **Directory**: `python-generators-0x00`
- **Files**:
  - `README.md`
  - `seed.py`
  - `0-main.py`
  - `user_data.csv`

## Usage

1. **Prerequisites**:
   - Install MySQL: `sudo apt install mysql-server`
   - Install Python MySQL connector: `pip install mysql-connector-python`
   - Configure MySQL root password.
2. **Setup**:
   - Download `user_data.csv`:
     ```bash
     wget "https://s3.amazonaws.com/alx-intranet.hbtn.io/uploads/misc/2024/12/3888260f107e3701e3cd81af49ef997cf70b6395.csv" -O user_data.csv
     ```
   - Set MySQL password in environment:
     ```bash
     export MYSQL_ROOT_PASSWORD="your_mysql_password"
     ```
3. **Run**:
   ```bash
   chmod +x 0-main.py
   ./0-main.py