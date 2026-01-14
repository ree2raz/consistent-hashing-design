"""
the data lives directly in the array. We have to handle "tombstones" (deleted markers), but we'll focus on insertion logic here.
"""

class LinearProbingHash:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.table = [None] * self.capacity # Flat array

    def insert(self, key, value):
        if self.size / self.capacity >= 0.75:
            self._resize()

        index = hash(key) % self.capacity

        # Linear Probing Logic
        while self.table[index] is not None:
            if self.table[index][0] == key: # Update existing key
                self.table[index] = (key, value)
                return
            index = (index + 1) % self.capacity # Move to next slot
        
        self.table[index] = (key, value)
        self.size += 1