"""
This is the "pro" version of Linear Probing. We track the DIB (Distance from Initial Bucket). If a new entry is "poorer" (further from its home) than the current resident, it steals the spot.
"""


class RobinHoodHash:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        # Store as (key, value, distance_from_home)
        self.table = [None] * self.capacity

    def insert(self, key, value):
        if self.size / self.capacity >= 0.75:
            self._resize()

        # Initial state of the element we want to insert
        curr_key, curr_val = key, value
        curr_dist = 0
        index = hash(key) % self.capacity

        while True:
            # 1. Found an empty slot? Put it there and exit.
            if self.table[index] is None:
                self.table[index] = (curr_key, curr_val, curr_dist)
                self.size += 1
                return

            # 2. Found the same key? Update and exit.
            if self.table[index][0] == curr_key:
                self.table[index] = (curr_key, curr_val, curr_dist)
                return

            # 3. Collision Logic: Who is "poorer"?
            existing_key, existing_val, existing_dist = self.table[index]

            if curr_dist > existing_dist:
                # The NEW element is further from home than the EXISTING one.
                # ROB FROM THE RICH: Swap them!
                self.table[index] = (curr_key, curr_val, curr_dist)
                
                # Now we need to find a new home for the displaced element
                curr_key, curr_val, curr_dist = existing_key, existing_val, existing_dist

            # Move to the next slot and increment distance
            index = (index + 1) % self.capacity
            curr_dist += 1