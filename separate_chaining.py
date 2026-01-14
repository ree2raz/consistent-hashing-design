"""
This is the most "stable" version. Even if the hash function is mediocre, the table won't break; it just gets slightly slower.
"""

class ChainingHash:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        # Each bucket is a list (simulating a Linked List)
        self.table = [[] for _ in range(self.capacity)]
        self.load_factor_threshold = 0.75

    def _hash(self, key):
        # Using Python's built-in SipHash and modding by capacity
        return hash(key) % self.capacity

    def insert(self, key, value):
        # 1. Check if we need to resize before adding
        if self.size / self.capacity >= self.load_factor_threshold:
            self._resize()

        index = self._hash(key)
        bucket = self.table[index]

        # 2. Check if key already exists (Update logic)
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        # 3. Collision handling: Just append to the list
        bucket.append((key, value))
        self.size += 1

    def _resize(self):
        old_table = self.table
        self.capacity *= 2
        self.table = [[] for _ in range(self.capacity)]
        self.size = 0
        
        # Rehash every single element into the new larger table
        for bucket in old_table:
            for k, v in bucket:
                self.insert(k, v)