"""
Naive Hashing shows the problem of collision and clustering
"""

# def naive_hash(key, table_size):
#     # This has terrible entropy. 
#     # "abc" and "cba" produce the exact same hash (Collision).
#     # "ab" and "ac" are only 1 unit apart (Clustering).
#     return sum(ord(char) for char in key) % table_size

# print(naive_hash("johndoe", 26))
# print(naive_hash("jondoe", 26))
# print(naive_hash("jonboe", 26))


"""
Python 3 actually uses SipHash 1-3 (as of version 3.11) or SipHash 2-4 (older versions) by default for its internal hash() function for strings and bytes.

However, Python's hash() is randomized every time you restart the interpreter (to prevent attacks).
"""
# We use a 128-bit key (16 bytes)
import hashlib
import os

# 1. Define the data
data = "user_1".encode('utf-8')

# 2. In a real system, this secret key prevents HashDoS attacks.
# Python's built-in hash() does this internally with a random seed.
secret_key = b'\x00' * 16 

# 3. Simulate the hashing process
# Note: Many systems use 'hashlib' or C-extensions for raw SipHash
def get_siphash(key, message):
    # Using a common third-party equivalent or built-in hash logic
    # Here we use the built-in hash() for simplicity, which IS SipHash
    return hash(message)

print(f"Python Hash: {hex(get_siphash(secret_key, data))}")