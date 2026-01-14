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

