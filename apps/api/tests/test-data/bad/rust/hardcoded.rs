// Bad: Hardcoded secrets

// rust-security-001
const API_KEY: &str = "sk_live_secret123";
const PASSWORD: &[u8] = b"admin@123";
