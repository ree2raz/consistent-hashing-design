import hashlib
import bisect
import mmh3

class ConsistentHashRing:
    def __init__(self, nodes=None, vnodes=100):
        """
        Initializes the hash ring.
        :param nodes: List of physical node names (e.g., ['server-1', 'server-2'])
        :param vnodes: Number of virtual nodes per physical node to ensure uniform distribution.
        """
        self.vnodes = vnodes
        
        # This list stores the sorted hash values of all virtual nodes (the 'Ring').
        self.ring = []        
        
        # Map to link a specific hash value back to the actual physical node name.
        self.nodes_map = {}   

        # If an initial list of nodes is provided, populate the ring immediately.
        if nodes:
            for node in nodes:
                self.add_node(node)

    # def _hash(self, key):
    #     """
    #     Generates a 128-bit integer hash for a given string key.
    #     We use MD5 for stability across different processes/restarts.
    #     """
    #     return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def _hash(self, key):
        # mmh3.hash returns a 32-bit integer by default. 
        # It's non-cryptographic, lightning fast, and has high entropy.
        return mmh3.hash(key)

    def add_node(self, node_name):
        """
        Places a physical node on the ring by creating multiple virtual nodes (vnodes).
        """
        for i in range(self.vnodes):
            # Create a unique string for each virtual node (e.g., "server-1#0", "server-1#1")
            vnode_key = f"{node_name}#{i}"
            h = self._hash(vnode_key)
            
            # bisect.insort maintains the list in sorted order (O(N) complexity for insertion).
            # This is efficient for setup/config changes, but lookups remain fast.
            bisect.insort(self.ring, h)
            
            # Store the mapping from the hash back to the physical node.
            self.nodes_map[h] = node_name

    def remove_node(self, node_name):
        """
        Removes all virtual nodes associated with a physical node.
        (Added this for completeness as it's vital for a dynamic system).
        """
        for i in range(self.vnodes):
            h = self._hash(f"{node_name}#{i}")
            # Find and remove the hash from the ring and the mapping.
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                self.ring.pop(idx)
                del self.nodes_map[h]

    def get_node(self, key):
        """
        Determines which physical node a specific key (e.g., user_id) belongs to.
        """
        if not self.ring:
            return None
        
        # 1. Hash the incoming key to find its position on the ring.
        h = self._hash(key)
        
        # 2. Use binary search (O(log N)) to find the first virtual node hash
        # that is greater than or equal to the key's hash.
        idx = bisect.bisect_left(self.ring, h)
        
        # 3. If the index is equal to the length of the ring, it means the key's hash
        # is larger than the largest hash in the ring. Because it's a 'ring',
        # we wrap around to the first node (index 0).
        idx = idx % len(self.ring)
        
        # 4. Return the physical node name associated with that hash.
        return self.nodes_map[self.ring[idx]]

"""
In a traditional hashing system hash(key) % N, adding one node causes roughly n-1/n (nearly 100%) of the keys to move. In consistent hashing, only about 1/n of the keys should move.

The Disruption Simulation
    We will:
        Initialize a ring with 3 nodes.
        Assign 10,000 keys to these nodes and record their locations.Add a 4th node.
        Re-assign the same 10,000 keys and see how many changed their "home" server.

Why this matters for your System Design ?
When you run this script, you'll see the disruption is likely around 20-25%.
- Weighting: In a real-world high-pace startup environment, your servers might not be identical. You can modify add_node to accept a weight parameter. A server with $2\times$ RAM could have vnodes * weight virtual nodes to handle double the traffic.
- Replication: Consistent hashing only tells you the "Primary" node. For high availability, you usually pick the next $N$ unique nodes clockwise on the ring to store replicas of the data.
- Collision Handling: While MD5 is stable, it's technically possible (though astronomically rare) for two vnodes to have the same hash. In production code, you should check if h already exists in nodes_map before inserting.
"""


def run_simulation():
    # 1. Setup initial cluster
    initial_nodes = ["Server_A", "Server_B", "Server_C"]
    ring = ConsistentHashRing(nodes=initial_nodes, vnodes=100)
    
    # 2. Map 10,000 keys to their initial nodes
    total_keys = 10000
    key_mapping_before = {}
    for i in range(total_keys):
        key = f"user_data_key_{i}"
        key_mapping_before[key] = ring.get_node(key)
        
    print(f"Initial State: 10,000 keys distributed across {initial_nodes}")
    
    # 3. Add a new node (Scaling Up)
    new_node = "Server_D"
    ring.add_node(new_node)
    print(f"Scaling Up: Added {new_node}")
    
    # 4. Check how many keys moved
    moved_keys = 0
    for key, old_node in key_mapping_before.items():
        new_node_assignment = ring.get_node(key)
        if new_node_assignment != old_node:
            moved_keys += 1
            
    # 5. Report results
    percentage_moved = (moved_keys / total_keys) * 100
    print("-" * 30)
    print(f"Total Keys: {total_keys}")
    print(f"Keys Moved: {moved_keys}")
    print(f"Disruption: {percentage_moved:.2f}%")
    
    # Theoretical disruption for 4 nodes should be ~25% (1/N)
    # Traditional mod N hashing would have been ~75% to 100%

if __name__ == "__main__":
    run_simulation()