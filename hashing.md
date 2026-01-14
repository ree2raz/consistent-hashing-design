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

In **Python**, because everything is an object (pointers), the `dict` implementation uses a very clever version of Open Addressing. In **Rust**, the standard `HashMap` uses **Control Bytes** (SIMD instructions) to check 16 buckets at once—taking the "Cache King" strategy to the extreme.

### Key Takeaways for your Engineering Portfolio:

- Chaining is easy to implement but punishes the CPU with random memory access (Cache Misses).
  - The Mechanism: When the CPU needs data, it doesn't just grab 8 bytes. It grabs a 64-byte "Cache Line" from RAM and puts it into the L1 Cache.
  - In Chaining, the "buckets" are usually Linked Lists. Each node in a linked list is allocated dynamically on the Heap. These nodes are scattered all over your RAM.
  - The "Punishment": To traverse a chain of 3 items, the CPU has to:
    - Look at the pointer in the main table (Fetch 1).
    - Jump to a random RAM address for Node A (Fetch 2).
    - Jump to another random RAM address for Node B (Fetch 3).
  - Each "jump" to a random address is a potential Cache Miss, forcing the CPU to sit idle for hundreds of cycles while the RAM fetches the data.

- Linear Probing is fast but suffers from "Clustering" — if one area gets busy, the whole table slows down. It has a "feedback loop" problem called Primary Clustering.
    - The Mechanism: If a collision occurs at index 5, you check 6. If 6 is full, you check 7.
    - The Logic of Failure: Imagine you have a cluster of occupied slots from index 5 to 9.
      - Any new key that hashes to 5, 6, 7, 8, or 9 will all end up being placed at index 10.
      - Now the cluster is 5 to 10.
      - The probability of hitting index 10 just increased from $1/Size$ to $6/Size$.
    - The Result: Clusters act like magnets. The larger a cluster gets, the faster it grows, leading to a massive "traffic jam" in one part of your array while other parts are empty. This turns your $O(1)$ lookup into a slow $O(n)$ crawl through the jam.

- Robin Hood Hashing fixes the clustering problem of Linear Probing. By swapping elements so that everyone is roughly the same distance from their "home" slot, you ensure that "Key Not Found" searches (the most expensive kind) fail quickly.
  - Robin Hood Hashing is essentially a "socialist" algorithm. It tries to minimize the variance of how far keys are from their original home.
  - Why it fixes Clustering:
    - In standard Linear Probing, the "first" person to arrive at a spot keeps it forever, even if someone else arrives later who is much further from home. In Robin Hood, if a "rich" element (one at its home index) is blocking a "poor" element (one 5 slots away from home), the poor element kicks the rich one out. By constantly re-shuffling to keep everyone's "Distance from Home" (DIB) roughly equal, you prevent long, contiguous chains from forming in one spot.
  - Why "Key Not Found" is faster:
    - This is the clever part. In standard Linear Probing, if you are looking for a key, you have to keep searching until you find it OR you hit an empty slot. If the table is 90% full, you might scan 50 items before finding an empty slot.
    - In Robin Hood, you can stop much earlier using the "I am richer than you" rule:
      - You are looking for Key X. You are currently at a probe distance of 3.
      - You look at the current slot in the table. The element there has a probe distance of 1.
      - Conclusion: If Key X were in this table, it would have kicked this element out (because 3 > 1). Since it hasn't, Key X definitely does not exist. You can stop the search immediately without ever reaching an empty slot.

| Strategy | Performance Bottleneck | Logical Stopping Point |
| --- | --- | --- |
**Chaining**|RAM Latency (Pointer Chasing)|End of the linked list.
**Linear Probing**|Algorithmic (Clustering)|Must find an empty slot.
**Robin Hood**|Minimal (Sorted-ish Probing)|Stop when current DIB < your DIB.

### Laymen Visualizations of the Algorithms to prevent Hashing Collisions

I hear you. When you're used to high-level abstractions, the leap down to how bits and CPU caches interact can feel like a jump into a dark room.

Let's take this slow. Imagine we have a **Hash Table with only 5 slots** (Indices 0 to 4).

### The Setup

* **Table Size ():** 5
* **Hash Function:** `key % 5` (Modulo)
* **Data to Insert:**
1. `"Alice"` (Hash 12  index **2**)
2. `"Bob"` (Hash 7  index **2**) — **COLLISION!**
3. `"Charlie"` (Hash 22  index **2**) — **TRIPLE COLLISION!**


### Scenario 1: Separate Chaining (The "Vertical" Approach)

Think of this like a **coat rack**. Each slot is a hook. If multiple coats belong on hook #2, you just hang them one on top of the other.

#### 1. The Insertion Process:

* **Alice (Index 2):** Put Alice at index 2.
* **Bob (Index 2):** Slot 2 is taken. We create a "link" from Alice to Bob.
* **Charlie (Index 2):** Slot 2 is still the target. We link Bob to Charlie.

#### 2. The Lookup (Finding Charlie):

1. Go to Index 2.
2. Is it Charlie? No, it's Alice. Follow the pointer to the next memory address.
3. Is it Charlie? No, it's Bob. Follow the pointer to the next memory address.
4. Found Charlie!

#### Why the "Cache Miss" happens here:

Imagine Alice is stored at memory address `1000`. When the CPU looks at Alice, it fetches the surrounding data (address `1000` to `1064`).
But **Bob** was created 10 minutes later, so the computer put him at address `9500`.
When the CPU finishes looking at Alice and needs Bob, it looks at the pointer and realizes Bob is at `9500`. **Address 9500 is not in the cache.** The CPU has to stop everything and wait for the RAM to find address 9500. This is the "Punishment."

### Scenario 2: Linear Probing (The "Next Door" Approach)

Think of this like a **parking lot**. If your reserved spot is taken, you just drive to the very next available spot.

#### 1. The Insertion Process:

* **Alice (Index 2):** Slot 2 is empty. Park Alice there.
* **Bob (Index 2):** Slot 2 is full! Go to the next spot: **Index 3**. It’s empty. Park Bob there.
* **Charlie (Index 2):** Slot 2 is full. Check 3. Slot 3 is full! Check **Index 4**. It’s empty. Park Charlie there.

#### 2. The Lookup (Finding Charlie):

1. Go to Home (Index 2). It's Alice.
2. Look "Next Door" (Index 3). It's Bob.
3. Look "Next Door" (Index 4). Found Charlie!

#### Why "Clustering" is a problem:

Imagine a fourth person, **Dave**, hashes to **Index 3**. Even though Dave's "Home" is index 3, he has to wait behind the "traffic jam" caused by Alice's collisions at Index 2. He'll end up at Index 0 (looping around). The parking lot gets "clumped" with cars, and everyone has to walk further and further to find a spot.

#### Why the "Cache Hit" happens here:

In the parking lot, all spots (0, 1, 2, 3, 4) are right next to each other in memory. When the CPU fetches Alice at Index 2, it **automatically** grabs Bob (Index 3) and Charlie (Index 4) because they are within that same 64-byte block. The CPU doesn't have to wait for RAM; the data is already inside the CPU.

### Scenario 3: Robin Hood Hashing (The "Fairness" Approach)

This is Linear Probing, but with a "kick-out" rule based on **Distance from Home (DIB)**.

#### 1. The Insertion Process:

* **Alice (Index 2):** DIB = 0 (She is at home). Park her.
* **Bob (Index 2):** Slot 2 is full. Bob moves to Index 3. His DIB is now **1**. Slot 3 is empty. Park him.
* **Charlie (Index 2):** 1. Check Index 2 (Alice). Her DIB is 0. Charlie's DIB would be 0. Charlie is not "poorer" than Alice. Move on.
2. Check Index 3 (Bob). **Bob's DIB is 1.** If Charlie were here, his DIB would be **1**. They are equal. Move on.
3. Check Index 4. Empty. Park Charlie. (DIB = 2).

#### The "Kick-Out" (The "Robbing" part):

Imagine **Zeke** hashes to **Index 4**.

1. Zeke goes to Index 4. **Charlie** is there.
2. **Charlie's DIB is 2** (He is 2 spots from home).
3. **Zeke's DIB is 0** (He is at his home).
4. Zeke is "Rich" (DIB 0), Charlie is "Poor" (DIB 2). Zeke says "Sorry, you're doing okay," and moves to Index 0.

**BUT**, if Zeke had arrived with a DIB of **5** and Charlie had a DIB of **2**, Zeke would **KICK CHARLIE OUT**, take the spot, and make Charlie go find a new home.

#### Why this helps "Not Found" lookups:

Imagine you are looking for **"Waldo"** who hashes to **Index 2**.

1. Check Index 2: Alice is there (DIB 0). You (Waldo) would have DIB 0. Keep looking.
2. Check Index 3: Bob is there (DIB 1). You (Waldo) would have DIB 1. Keep looking.
3. Check Index 4: You see an element with **DIB 0**.
4. **STOP!** You know Waldo isn't here.
* *Logic:* If Waldo existed, his DIB at this spot would be **2**. Since the guy currently here is "Richer" than Waldo (DIB 0), and we know we always put the "Poorest" people further down the line, Waldo **must not exist**.


| Strategy | Mental Image | Why it’s fast | Why it’s slow |
| --- | --- | --- | --- |
| **Chaining** | A coat rack with hangers. | Easy to add items. | CPU has to jump all over RAM. |
| **Linear Probing** | A parking lot. | Everything is in one row (Cache). | Huge traffic jams (Clustering). |
| **Robin Hood** | A parking lot with a bully. | Balanced distances. | Slightly more complex logic to insert. |

### Systems Architect's Cheat Sheet.

These principles ensure that your distributed system remains balanced, fast, and resilient. 🚀

### 🏛️ The Three Pillars of Hashing for Distributed Systems

| Pillar | Concept | Real-World Application 🌍 |
| --- | --- | --- |
| **Uniformity** ⚖️ | High-entropy functions (SipHash, MurmurHash) ensure data is spread evenly. | Prevents "Hot Spots" where one server in your ring gets 90% of the traffic. |
| **Determinism** 🎯 | The same input MUST yield the same output every time. | Ensures that if User A is mapped to Server 1, they stay there unless the ring changes. |
| **Efficiency** ⚡ | Low latency and  lookups. | Minimizes the overhead added to every request in your microservices. |

---

### 🛠️ Key Implementation Lessons

1. **The Modulo Bottleneck** 🛑: Traditional hashing uses . In a distributed system, if  (number of servers) changes, **every single key** maps to a new location. This is why we move toward **Consistent Hashing**, which minimizes this data movement.
2. **Collision Resolution** ⚔️: While we discussed **Chaining** and **Open Addressing** for local memory, in distributed systems, collisions often manifest as "Key Overlap." We use high-bit hashes (128-bit or 256-bit) to make the mathematical probability of a collision effectively zero.
3. **The Cache Factor** 🧠: Just as CPU caches prefer contiguous memory, distributed systems prefer "Data Locality." Using a consistent hash ring helps keep related data on the same node, reducing network "hops." 🛰️

---

### 🏗️ Moving Toward Hash Rings

When building a Hash Ring, you aren't just mapping a key to an array index. You are mapping both **Keys** and **Servers** onto a 360° abstract circle. ⭕

To see if we’re ready for the "Ring" logic, let's think about the **Rehash** problem we discussed earlier.

**In a standard hash table, if we double the size (), we have to move almost all the data. In a distributed system with 100 servers, if we add 1 new server, what do you think would be the "ideal" amount of data to move to keep the system efficient?** :
**In a distributed system, if you have 100 servers and add 1 more, the "ideal" scenario is to only move 1/101th of your data.**
