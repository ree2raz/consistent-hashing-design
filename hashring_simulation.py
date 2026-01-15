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
        """Adds a physical node with a specific weight by scaling vnodes."""
        self.weights[node_name] = weight
        effective_vnodes = int(self.vnodes * weight)
        
        for i in range(effective_vnodes):
            vnode_key = f"{node_name}#{i}"
            h = self._hash(vnode_key)
            
            # Handle rare hash collisions in the ring
            while h in self.nodes_map:
                vnode_key += "_collision"
                h = self._hash(vnode_key)
                
            bisect.insort(self.ring, h)
            self.nodes_map[h] = node_name

    def remove_node(self, node_name):
        """Dynamically removes all virtual nodes associated with a physical node."""
        if node_name not in self.weights:
            return
        
        weight = self.weights.pop(node_name)
        effective_vnodes = int(self.vnodes * weight)
        
        for i in range(effective_vnodes):
            vnode_key = f"{node_name}#{i}"
            h = self._hash(vnode_key)
            
            idx = bisect.bisect_left(self.ring, h)
            # Standard cleanup of the ring and map
            if idx < len(self.ring) and self.ring[idx] == h:
                self.ring.pop(idx)
                self.nodes_map.pop(h, None)

    def get_nodes(self, key, n=2):
        """Returns the next 'n' unique physical nodes clockwise on the ring."""
        if not self.ring: return []
        
        h = self._hash(key)
        start_idx = bisect.bisect_left(self.ring, h)
        
        targets = []
        # Linear probe clockwise to find N unique physical nodes
        for i in range(len(self.ring)):
            idx = (start_idx + i) % len(self.ring)
            node_name = self.nodes_map[self.ring[idx]]
            
            if node_name not in targets:
                targets.append(node_name)
            
            if len(targets) == n:
                break
        return targets


class PhysicalNode:
    """Mock of a physical server instance with local storage."""
    def __init__(self, name):
        self.name = name
        self.storage = {}

    def put(self, key, value):
        self.storage[key] = value
        return f"[{self.name}] Saved '{key}'"

    def get(self, key):
        return self.storage.get(key, "MISS")


class Infrastructure:
    """Orchestrator for the ring and the physical server instances."""
    def __init__(self, replication_factor=2):
        self.ring = ConsistentHashRing()
        self.servers = {}
        self.rep_factor = replication_factor

    def deploy_server(self, name, weight=1):
        print(f"Deploying {name} (Weight: {weight})...")
        self.servers[name] = PhysicalNode(name)
        self.ring.add_node(name, weight)

    def fail_server(self, name):
        print(f"\n--- [CRITICAL FAILURE] {name} is offline ---")
        self.ring.remove_node(name)
        # In a real outage, local data on the failed server becomes unreachable
        del self.servers[name]

    def handle_request(self, key, value=None):
        """Unified entry point for PUT and GET requests with replication logic."""
        targets = self.ring.get_nodes(key, n=self.rep_factor)
        
        if not targets:
            return "Error: No Infrastructure available."

        # If value is provided, it's a WRITE (PUT)
        if value:
            responses = []
            print(f"Routing '{key}' to replicas: {targets}")
            for t in targets:
                responses.append(self.servers[t].put(key, value))
            return " | ".join(responses)
        
        # Otherwise, it's a READ (GET)
        # Simple Failover: try each replica in order until we find the data
        for t in targets:
            if t in self.servers:
                res = self.servers[t].get(key)
                if res != "MISS":
                    return f"(Success from {t}) Query '{key}': {res}"
        
        return f"(Total Failure) Query '{key}': Data lost on all {len(targets)} replicas."

# --- Full Simulation ---

def main():
    # Set replication factor to 2. This ensures data survives a single node failure.
    infra = Infrastructure(replication_factor=2)
    
    # 1. Setup heterogeneous nodes
    infra.deploy_server("Node-Standard", weight=1)
    infra.deploy_server("Node-Prime", weight=4)
    
    # 2. Distribute Workload
    print("\n--- Phase 1: Weighted Distribution with Replication ---")
    keys = [f"request_id_{i}" for i in range(5)]
    for k in keys:
        # Data will be written to both Node-Prime AND Node-Standard
        print(infra.handle_request(k, value="Payload_Data"))

    # 3. Trigger Failure
    # We kill Node-Prime, which was holding the majority of the data.
    infra.fail_server("Node-Prime")

    # 4. Check Retrieval & Re-routing
    print("\n--- Phase 2: Failure Recovery (Zero Data Loss) ---")
    for k in keys:
        # Even though Node-Prime is dead, Node-Standard has the replica.
        print(infra.handle_request(k))

if __name__ == "__main__":
    main()