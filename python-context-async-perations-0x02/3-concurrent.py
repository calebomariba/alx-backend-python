#!/usr/bin/env python3
import asyncio
import aiosqlite

async def async_fetch_users():
    """Fetch all users from the users table asynchronously."""
    try:
        async with aiosqlite.connect("users.db") as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users") as cursor:
                results = await cursor.fetchall()
                return [tuple(row) for row in results]
    except aiosqlite.Error as e:
        print(f"Error fetching users: {e}")
        return []

async def async_fetch_older_users():
    """Fetch users older than 40 from the users table asynchronously."""
    try:
        async with aiosqlite.connect("users.db") as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
                results = await cursor.fetchall()
                return [tuple(row) for row in results]
    except aiosqlite.Error as e:
        print(f"Error fetching older users: {e}")
        return []

async def fetch_concurrently():
    """Run both fetch queries concurrently and return results."""
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users(),
        return_exceptions=True
    )
    return all_users, older_users

# Example usage
if __name__ == "__main__":
    try:
        all_users, older_users = asyncio.run(fetch_concurrently())
        print("All users:")
        for user in all_users:
            print(user)
        print("\nUsers older than 40:")
        for user in older_users:
            print(user)
    except Exception as e:
        print(f"Error running concurrent queries: {e}")