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

### High Scale Production Implementation 

#### High-Entropy Hash algorithm

- SipHash or MurmurHash3 to ensure keys are distributed uniformly to prevent "organic" collisions.
- In a high-pace production environment, a "bad" hash function doesn't just slow things down—it creates a security vulnerability called a `HashDoS` attack, where an attacker intentionally sends keys that collide, turning your $O(1)$ lookup into $O(n)$.
- Entropy in this context refers to the randomness and unpredictability of the hash output. A high-entropy hash function ensures that even if two inputs are nearly identical (e.g., user_1 and user_2), their outputs are mathematically uncorrelated.
  - The "Avalanche Effect" : If you change exactly one bit in the input, each bit in the output should have a 50% chance of changing. Every mathematically sound hash must satisfy this, $$P(\text{bit}_i \text{ flips} \mid \text{input change}) \approx 0.5$$
  - If your hash function lacks this, you get clustering.
    - Low Entropy: hash("key1") = 100, hash("key2") = 101. Both keys land in the same neighborhood of the array.
    - High Entropy: hash("key1") = 100, hash("key2") = 9223372036854775807. The keys are scattered across the entire memory space.

| Algorithm | Primary Strength | Use Case |
| --- | --- | --- |
**MurmurHash3**|**Speed.** It’s non-cryptographic and incredibly fast at mixing bits.|Databases (Cassandra), Load Balancers, Bloom Filters.
**SipHash**|**Security.** It is "keyed," meaning it uses a secret seed.|Programming language internals (Rust/Python/Ruby) to prevent HashDoS.

#### The "Secret Seed" (The Pro Move)
If an attacker knows you are using MurmurHash3, they can pre-calculate thousands of strings that all hash to the same bucket.SipHash prevents this by using a random seed generated when your program starts:$$Hash = SipHash(Key, \text{Random\_Seed})$$Because the attacker doesn't know your Random_Seed, they cannot predict which keys will collide, making their attack impossible.


### The Load Factor & Rehash ()

The **Load Factor ()** is the measure of how "crowded" your hash table is. It is defined by the formula:

Where:

*  = Number of entries currently in the table.
*  = Total number of slots (buckets).

#### Why 0.75?

If , the table is full. In a perfect world, you’d have one item per slot. In reality, as  approaches 1.0, the probability of **collisions** skyrockets.

* **Math:** In Linear Probing, the expected number of probes for a successful search is approximately .
* At **0.50**, you expect 1.5 probes.
* At **0.90**, you expect 5.5 probes.
* The industry standard of **0.75** is the "sweet spot" where you maximize memory usage without significantly degrading the  lookup time.

#### The "Resize/Rehash" Operation

When your code does `map.insert(key, value)` and the load factor hits 0.76, the map doesn't just grow like a list. It performs a **Rehash**:

1. **Allocate** a new array (usually **2x** the current size).
2. **Iterate** through every single item in the old array.
3. **Recalculate** the hash for every key (because the modulo `index % size` has changed).
4. **Insert** them into the new, larger array.

**Startup Warning:** Rehing is an  operation. If you have 10 million items, a rehash will cause a "latency spike." In high-pace systems, we often "pre-allocate" the capacity if we know how much data is coming to avoid this.

---

### Strategy: Open Addressing vs. CPU Cache

This is a deep-dive into how hardware affects software.

#### The CPU Cache (L1/L2/L3)

Modern CPUs are thousands of times faster than RAM. To stay fast, they fetch "cache lines" (usually 64 bytes of data) from RAM into the CPU cache.

* If your data is **contiguous** (next to each other in memory), the CPU "pre-fetches" it. This is a **Cache Hit**.
* If your data is scattered (jumping to different memory addresses), the CPU stalls while waiting for RAM. This is a **Cache Miss**.

#### Open Addressing: The "Cache King"

In Open Addressing (like Python's `dict`), everything is in one flat array.

* **The Benefit:** When the CPU looks for a key at `index 5` and it's a collision, it checks `index 6`. Because `6` is right next to `5`, it is almost certainly already in the CPU cache.
* **Best for:** Small keys/values (integers, small strings) that fit neatly inside that 64-byte cache line.

#### Chaining: The "Heavy Object" Choice

In Chaining (like Java’s `HashMap`), each slot is a pointer to a **Linked List** elsewhere in memory.

* **The Problem:** Every time you follow a pointer to the next node in the list, you risk a **Cache Miss**. The data is scattered all over the RAM.
* **The Benefit:** If your "Value" is a massive 2KB object, moving it during a **Resize/Rehash** in Open Addressing is expensive because you have to copy 2KB of data to a new memory location.
* **In Chaining**, you only move the **8-byte pointer**. The heavy 2KB object stays exactly where it was in memory.

---

### Summary Table for Implementation

| Scenario | Recommended Strategy | Why? |
| --- | --- | --- |
| **High Frequency Trading** | Open Addressing (Linear Probing) | Every nanosecond counts; cache hits are mandatory. |
| **Large Metadata Storage** | Chaining | Objects are too big to move; resizing would be too slow. |
| **Untrusted Public API** | SipHash + Chaining | Protects against HashDoS; scales better under heavy collision. |
| **Embedded / IoT** | Open Addressing | Lower memory overhead (no extra pointers/nodes). |

### Final Practical Tip

In **Python**, because everything is an object (pointers), the `dict` implementation uses a very clever version of Open Addressing. In **Rust**, the standard `HashMap` uses **Control Bytes** (SIMD instructions) to check 16 buckets at once—taking the "Cache King" strategy to the extreme.
