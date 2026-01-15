import hashlib
import bisect

class ConsistentHashRing:
  def __init__(self, nodes=None, vnodes=100):
    self.vnodes = vnodes
    # Sorted list of virtual nodes hashes
    self.ring = [] 
    # Maps hash -> Physical node name
    self.nodes_map = {}

    if nodes:
      for node in nodes:
        self.add_node(node)

  def _hash(self, key):
    """Standardizing the hash function"""
    return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
  
  def add_node(self, node_name):
    """Adds a physical node and its virtual replicas to the ring"""
    for i in range(self.vnodes):
      vnode_key = f"{node_name}#{i}"
      vnode_hash = self._hash(vnode_key)
      
      # 1. How do we keep self.ring sorted while adding ?
      # Add to the sorted ring using bisect.insort
      bisect.insort(self.ring, vnode_hash)
      
      # 2. How do we link this hash back to the node_name ?
      # Map the hash back to the physical node
      self.nodes_map[vnode_hash] = node_name

  def get_node(self, request_key):
    """Finds the 'closest' node clockwise for a given key"""
    if not self.ring:
      return None

    key_hash = self._hash(request_key)
    
    # 3. How do we find the first element in self.ring >= key_hash ?
    # Binary search for the first virtual node hash >= key_hash
    idx = bisect.bisect_left(self.ring, key_hash)

    # 4. What happens if key_hash is larger than the last element in the ring ?
    # Handle the wrap-around using modulo
    actual_idx = idx % len(self.ring)

    # Retrieve the physical node name
    return self.nodes_map[self.ring[actual_idx]]


