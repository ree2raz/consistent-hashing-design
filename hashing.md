# What is Hashing ? 

It is the process of transforming any given input (a string, a file, a number) into a fixed-size string of characters, typically a hexadecimal number. Think of it as creating a "digital fingerprint" for data.

### How it Works: The Hash Function 

A hash function is a mathematical algorithm that maps data of arbitrary size to data of a fixed size. For a hash function to be effective in computer science, it must follow three rules:

- Deterministic: The same input must always produce the exact same output
- Collision Resistant: It should be extremely rare for two different inputs to produce the same hash output.
- Efficient yet Irreversible: It should be fast to compute the hash however shouldn't be able to reconstruct the original input from the output.

### Why is Hashing Important ?

Hashing is one of the most fundamental concepts in software engineering because it solves problems related to speed, security, and data integrity.

1. Constant Time Data Retrieval `O(1)` : (Hash Map / Table) By hashing a `key`, we get an index. This allows us to jump directly to the memory location.
2. Password Security : It is standard practice to store sensitive plain text data like passwords in hashed form in databases.
3. Data Integrity and Deduplication : We check integrity of downloaded files using hashes so that if what we intended to download has been corrupted even by a bit, the hashes will not match. Dropbox like cloud storage providers only keeps single copy of data that is duplicated among many users to avoid duplicated data taking space.
4. Distributed Systems and Blockchains : In a blockchain, each block contains a hash of the previous block, creating a chain. If a old block is altered, its hash changes, which breaks the hash of the next block, and the next, alerting the entire network to the tampering.

### Common Hashing Algorithms

| Algorithm | Type | Use Case |
| --- | --- | --- |
| **MD5** | Non-Cryptographic | Fast, used for checksums; now considered insecure for passwords. |
| **SHA-256** | Cryptographic | Standard for SSL certificates, Bitcoin, and file integrity. |
| **bcrypt / Argon2** | Cryptographic | Specifically designed for password hashing (intentionally slow to prevent brute-force). |
| **MurmurHash** | Non-Cryptographic | Extremely fast; used in hash tables and databases for lookups. |

### The "Collision" Problem

A collision occurs when two different inputs produce the same hash. While theoretically possible (because there are infinite inputs but finite hash outputs), a good hash function makes this statistically impossible for practical purposes. In software engineering, when a collision happens in a hash map, we use techniques like `Chaining` (linked lists at that index) or `Open Addressing` to handle it.

In any high-performance system, the "birthday paradox" is real: collisions aren't a "maybe," they are a "when." Since a hash table maps a massive universe of keys into a finite array of buckets, two keys will eventually land in the same spot. Fixing this isn't just about "making it work"; it’s about maintaining `O(1)` performance and cache efficiency.

### Methods to avoid hash collision

- Separate Chaining (The "Bucket" Approach)
  - In this method, each slot in the hash table doesn't store the data directly. Instead, it holds a pointer to a secondary data structure (usually a Linked List) that stores all elements hashing to that same index.
    - How it works: When a collision occurs, you simply append the new key-value pair to the list at that index.
    - Modern Optimization (Treeification): Standard linked lists are $O(n)$ to search. If a single bucket gets slammed with collisions (e.g., during a HashDoS attack), performance collapses. Java 8+ handles this by "treeifying" the bucket: once a list exceeds 8 elements, it converts the linked list into a Red-Black Tree, bringing worst-case lookup down from $O(n)$ to $O(\log n)$.

- Open Addressing (The "Probing" Approach)
  - Unlike chaining, all elements are stored directly in the main array. If a slot is taken, the system "probes" for the next available one. This is the preferred method for languages like Python and Rust because it is incredibly cache-friendly (data stays in contiguous memory).
    - A. Linear Probing : If index is full, try index + 1, then index + 2, and so on.
      - Pros: Best cache locality; the CPU can pre-fetch the next slots easily.
      - Cons: Primary Clustering. If many keys hash to the same area, you get "clumps" of occupied slots, making every subsequent search or insert much slower.
    - B. Quadratic Probing: Instead of checking the next slot, you check $i^2$ (e.g., $1, 4, 9, 16$).
      - Pros: Breaks up primary clusters.
      - Cons: Causes Secondary Clustering (keys that hash to the same spot still follow the same path).
    - C. Double Hashing : If a collision occurs, use a second hash function to determine the "step size" for probing.
      - Formula: $Index = (Hash1(key) + i \cdot Hash2(key)) \pmod{Size}$
      - Pros: Virtually eliminates clustering.
- **The Modern Gold Standard: Robin Hood Hashing**
  - Used in high-performance implementations (like Rust’s older HashMap and various C++ libraries), this is a sophisticated variant of Linear Probing.
  - The Logic: It **"robs from the rich and gives to the poor."** 
    - Every element tracks its Distance from Home (DFH) (how many slots it is away from its original hash index).
    - During an insertion, if the new element has a higher DFH than the element currently in the slot, the new element kicks out the existing one.
    - The displaced element then searches for a new home.
  - Why it’s better: It minimizes the "variance" of probe lengths. Instead of some keys being 0 slots away and others being 50, everyone ends up roughly 2–4 slots away. This makes "Key Not Found" searches much faster because you can stop searching as soon as you see an element "richer" than you.
