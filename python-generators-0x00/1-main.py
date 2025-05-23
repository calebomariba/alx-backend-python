#!/usr/bin/python3
from itertools import islice

# Import the module first
stream_users_module = __import__('0-stream_users')

# Access the function from the module
stream_users = stream_users_module.stream_users

# Use the generator function
for user in islice(stream_users(), 6):
    print(user)
