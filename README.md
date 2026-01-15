# Consistent Hashing

Consistent hashing is a special kind of hashing such that when a hash table is re-sized and consistent hashing is used, only `k/n` keys need to be remapped on average, where `k` is the number of keys, and `n` is the number of slots. In contrast, in most traditional hash tables, a change in the number of array slots causes nearly all keys to be remapped.

## The Rehashing problem
If you have n cache servers, a common way to balance the load is to use the following hash method:
`serverIndex = hash(key) % N` where N is the size of the server pool.

- This works until you need to scale. If you have 4 servers and add 1 more `n=5`:
  - Almost every key's mapping changes `hash(key) % 4` vs `hash(key) % 5`. For e.g., `hash(key0) => 151011 % 4 => 3` while `hash(key0) => 151011 % 5 => 1`.
  - In a caching layer, this triggers a **cache stampede** because suddenly 80-90% of your keys are "missing" from their new assigned servers.
  - In a database, you’d have to migrate nearly all your data across the network.
- Consistent hashing ensures that when a node is added or removed, only `K/n` keys need to be remapped (where `K` is the total number of keys).


> **With simple hashing, when a new server is added, almost all the keys need to be remapped. With consistent hashing, adding a new server only requires redistribution of a fraction of the keys**

# 🚀 Consistent Hashing: High-Performance Distributed Scaling

## 📖 Overview

Consistent hashing is a distribution strategy that allows for horizontal scaling of distributed systems (Caches, NoSQL DBs, Load Balancers) with minimal data movement. Unlike standard modulo hashing, which causes a "global reshuffle" when nodes are added or removed, consistent hashing ensures that only **** keys are remapped.

### 🍕 The "Pizza Slice" Analogy

Imagine the hash space as a giant circular pizza.

* **Physical Nodes:** These are "cutters" placed at random points on the pizza edge.
* **Keys (Data):** These are "toppings" placed on the pizza. A topping belongs to the first cutter you hit moving **clockwise**.
* **Virtual Nodes:** Instead of 3 big cutters, we use 300 tiny ones. If one cutter is removed, its toppings are distributed among *many* other cutters, not just one neighbor.


## 🛠 Production Implementation (Python)

```python
import hashlib
import bisect

class ConsistentHashRing:
    def __init__(self, nodes=None, vnodes=100):
        self.vnodes = vnodes
        self.ring = []        # Sorted list of VNode hashes
        self.nodes_map = {}   # Mapping: Hash -> Physical Node
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        # Always use a stable hash like MD5/SHA; never use Python's hash()
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name):
        for i in range(self.vnodes):
            h = self._hash(f"{node_name}#{i}")
            bisect.insort(self.ring, h)
            self.nodes_map[h] = node_name

    def get_node(self, key):
        if not self.ring: return None
        h = self._hash(key)
        idx = bisect.bisect_left(self.ring, h) % len(self.ring)
        return self.nodes_map[self.ring[idx]]

```

## 🏗 System Design Deep Dive

### 1. Why Virtual Nodes (VNodes)?

* **Uniformity:** Prevents "hot spots" where one server owns a disproportionate slice of the ring.
* **Heterogeneity:** You can give powerful servers more VNodes (higher `weight`) to handle more traffic.
* **Blast Radius:** If a node fails, its load is spread across the *entire* remaining cluster.

### 2. The Replication Strategy 🛡️

In production (e.g., Cassandra or DynamoDB), we don't just store data on *one* node. We store it on the first  distinct nodes encountered clockwise on the ring. This ensures **High Availability**.

### 3. Edge Case: The "Wrap-Around"

If a key's hash is higher than the highest VNode hash, it "wraps around" to the first VNode at the start of the ring (index 0).


## 📚 Industry Standards

| Category | Names to Know |
| --- | --- |
| **Algorithms** | **Ketama** (used by Nginx/Memcached), **Jump Consistent Hash** (Google) |
| **Python Libs** | `uhashring` (standard), `sortedcontainers` (for custom high-speed rings) |
| **Systems** | **Amazon DynamoDB**, **Apache Cassandra**, **Akamai CDN**, **Discord** |

## ⚠️ Critical Things to Remember

1. **Deterministic Hashing:** Ensure all clients use the *exact same* hash algorithm and seed.
2. **Node Flapping:** Rapidly adding/removing nodes can cause "thrashing." Use a **Gossip Protocol** or centralized coordinator (Zookeeper/Etcd) to sync the ring state.
3. **Cascading Failures:** Without VNodes, a single node failure can double the load on its immediate neighbor, potentially killing it and starting a domino effect.

