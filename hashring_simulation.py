"""
It includes MurmurHash3 for entropy, Weighted Nodes for heterogeneous hardware, and a Resilient Cluster Manager to simulate real-world failure and request routing.
"""

import mmh3
import bisect

class ConsistentHashRing:
    def __init__(self, vnodes=100):
        """
        :param vnodes: Base number of virtual nodes per physical node.
        """
        self.vnodes = vnodes
        self.ring = []        # Sorted list of VNode hashes (The Ring)
        self.nodes_map = {}   # Mapping: Hash -> Physical Node Name
        self.weights = {}     # Track weights for correct removal

    def _hash(self, key):
        """High-entropy non-cryptographic hash for speed and distribution."""
        return mmh3.hash(key)

    def add_node(self, node_name, weight=1):
        """Adds a physical node with a specific weight."""
        self.weights[node_name] = weight
        effective_vnodes = int(self.vnodes * weight)
        
        for i in range(effective_vnodes):
            vnode_key = f"{node_name}#{i}"
            h = self._hash(vnode_key)
            
            # Handle rare hash collisions
            while h in self.nodes_map:
                vnode_key += "_collision"
                h = self._hash(vnode_key)
                
            bisect.insort(self.ring, h)
            self.nodes_map[h] = node_name

    def remove_node(self, node_name):
        """Dynamically removes a node from the ring."""
        if node_name not in self.weights:
            return
        
        weight = self.weights.pop(node_name)
        effective_vnodes = int(self.vnodes * weight)
        
        for i in range(effective_vnodes):
            vnode_key = f"{node_name}#{i}"
            # We must account for the collision salt if we used it in a real system,
            # but for this simulation, we'll re-calculate the hash.
            h = self._hash(vnode_key)
            
            # Find and remove from the ring
            idx = bisect.bisect_left(self.ring, h)
            if idx < len(self.ring) and self.ring[idx] == h:
                self.ring.pop(idx)
                self.nodes_map.pop(h, None)

    def get_node(self, key):
        """Finds the node responsible for the key (Clockwise search)."""
        if not self.ring: return None
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, h) % len(self.ring)
        return self.nodes_map[self.ring[idx]]


class PhysicalNode:
    """Simulates a server with internal storage."""
    def __init__(self, name):
        self.name = name
        self.data = {}

    def put(self, key, value):
        self.data[key] = value
        return f"[{self.name}] Saved '{key}'"

    def get(self, key):
        val = self.data.get(key, "MISS (Data Lost/Not Found)")
        return f"[{self.name}] Query '{key}': {val}"


class Infrastructure:
    """The 'Control Plane' managing nodes and routing."""
    def __init__(self):
        self.ring = ConsistentHashRing()
        self.servers = {}

    def deploy_server(self, name, weight=1):
        print(f"Deploying {name} (Weight: {weight})...")
        self.servers[name] = PhysicalNode(name)
        self.ring.add_node(name, weight)

    def fail_server(self, name):
        print(f"\n--- CRITICAL FAILURE: {name} is offline ---")
        self.ring.remove_node(name)
        # In a real outage, the data on the failed server is unreachable
        del self.servers[name]

    def request(self, key, value=None):
        target = self.ring.get_node(key)
        if not target: return "Error: No Infrastructure"
        
        server = self.servers[target]
        if value:
            return server.put(key, value)
        return server.get(key)

# --- Full Simulation ---

def main():
    infra = Infrastructure()
    
    # 1. Weighted Setup
    # Node-Prime is 4x beefier than Node-Standard
    infra.deploy_server("Node-Standard", weight=1)
    infra.deploy_server("Node-Prime", weight=4)
    
    # 2. Distribute Workload
    print("\n--- Phase 1: Weighted Distribution ---")
    keys = [f"request_id_{i}" for i in range(10)]
    for k in keys:
        print(infra.request(k, value="Payload_Data"))

    # 3. Trigger Failure
    # Let's say Node-Prime crashes
    infra.fail_server("Node-Prime")

    # 4. Check Retrieval & Re-routing
    print("\n--- Phase 2: Failure Re-routing ---")
    for k in keys:
        # If the key was on Node-Prime, it will now hit Node-Standard.
        # It will be a MISS because Node-Standard doesn't have Node-Prime's data.
        print(infra.request(k))

if __name__ == "__main__":
    main()