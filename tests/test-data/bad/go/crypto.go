package main

import (
	"crypto/md5"
	"crypto/sha1"
	"math/rand"
)

// BAD: go-crypto-001 — MD5 hash
// ruleid: go-crypto-001
func hashWithMD5(data []byte) []byte {
	h := md5.New()
	h.Write(data)
	return h.Sum(nil)
}

// ruleid: go-crypto-001
func checksumMD5(data []byte) [16]byte {
	return md5.Sum(data)
}

// BAD: go-crypto-001 — SHA1 hash
// ruleid: go-crypto-001
func hashWithSHA1(data []byte) []byte {
	h := sha1.New()
	h.Write(data)
	return h.Sum(nil)
}

// BAD: go-crypto-002 — math/rand for token generation
// ruleid: go-crypto-002
func generateToken() int {
	return rand.Intn(1000000)
}

// ruleid: go-crypto-002
func generateSessionID() int64 {
	return rand.Int63()
}
