// Bad: Weak cryptography

// kotlin-crypto-001, 002, 003
val md5 = MessageDigest.getInstance("MD5")
val weakKey = "hardcoded_key_12345"
val random = Random(System.currentTimeMillis())
val insecureBytes = random.nextBytes(16)
