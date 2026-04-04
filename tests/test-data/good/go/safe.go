package main

import (
	"crypto/rand"
	"crypto/sha256"
	"crypto/tls"
	"math/big"
	"net/http"
	"os"
	"path/filepath"

	"github.com/golang-jwt/jwt"
)

// GOOD: parametrized SQL query
func getUserByID(db *sql.DB, id string) {
	db.Query("SELECT * FROM users WHERE id = ?", id)
}

// GOOD: exec.Command with safe argument array (not sh -c)
func runSafeCommand(safeDir string) {
	exec.Command("ls", "-la", safeDir).Run()
}

// GOOD: filepath.Base sanitizes traversal before Join
func serveFile(w http.ResponseWriter, r *http.Request) {
	safe := filepath.Base(r.PathValue("file"))
	filePath := filepath.Join("/data", safe)
	http.ServeFile(w, r, filePath)
}

// GOOD: SHA-256 hash
func hashData(data []byte) []byte {
	h := sha256.New()
	h.Write(data)
	return h.Sum(nil)
}

// GOOD: crypto/rand for token
func generateToken() (*big.Int, error) {
	return rand.Int(rand.Reader, big.NewInt(1000000))
}

// GOOD: TLS with proper config
func secureHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{
			MinVersion: tls.VersionTLS12,
		},
	}
	return &http.Client{Transport: tr}
}

// GOOD: JWT secret from environment
func parseToken(tokenStr string) (*jwt.Token, error) {
	secret := os.Getenv("JWT_SECRET")
	return jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
		return []byte(secret), nil
	})
}

// GOOD: proper error handling
func readFile(filename string) ([]byte, error) {
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	data := make([]byte, 1024)
	_, err = f.Read(data)
	return data, err
}

// GOOD: http.Error instead of panic
func handler(w http.ResponseWriter, r *http.Request) {
	http.Error(w, "not implemented", http.StatusNotImplemented)
}

// GOOD: TLS server
func startServer(mux *http.ServeMux) error {
	return http.ListenAndServeTLS(":443", "cert.pem", "key.pem", mux)
}
