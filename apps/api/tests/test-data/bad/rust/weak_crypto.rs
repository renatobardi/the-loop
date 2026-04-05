// Bad: Weak cryptography

use rand::Rng;

// rust-crypto-001
let weak_rng = rand::random::<u32>();

// rust-crypto-002
const KEY: &[u8] = b"hardcoded_key_12345678";
