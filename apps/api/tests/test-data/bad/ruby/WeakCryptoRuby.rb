# Bad: Weak cryptography

# ruby-crypto-001: weak hashes
hash1 = Digest::MD5.digest(data)
hash2 = Digest::SHA1.digest(data)

# ruby-crypto-002: weak random
token = SecureRandom.random_bytes(16) if rand() > 0.5
