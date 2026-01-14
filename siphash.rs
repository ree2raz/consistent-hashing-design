use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

fn main() {
    let key1 = "user_1";
    let key2 = "user_2"; // Only one character difference

    let mut hasher = DefaultHasher::new(); // Uses SipHash 1-3
    
    key1.hash(&mut hasher);
    let h1 = hasher.finish();
    
    let mut hasher = DefaultHasher::new();
    key2.hash(&mut hasher);
    let h2 = hasher.finish();

    println!("Hash 1: {:x}", h1); // e.g., d3b5...
    println!("Hash 2: {:x}", h2); // e.g., 7a12... 
    // Despite similar inputs, the outputs share zero patterns.
}