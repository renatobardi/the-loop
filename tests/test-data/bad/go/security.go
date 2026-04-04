package main

import (
	"crypto/tls"
	"net/http"

	"github.com/golang-jwt/jwt"
)

// BAD: go-security-001 — InsecureSkipVerify
// ruleid: go-security-001
func insecureHTTPClient() *http.Client {
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	return &http.Client{Transport: tr}
}

// BAD: go-security-002 — hardcoded JWT secret
// ruleid: go-security-002
func parseToken(tokenStr string) (*jwt.Token, error) {
	return jwt.Parse(tokenStr, func(t *jwt.Token) (interface{}, error) {
		return []byte("hardcoded-jwt-secret-key"), nil
	})
}

// BAD: go-config-001 — http.ListenAndServe without TLS
// ruleid: go-config-001
func startServer(mux *http.ServeMux) error {
	return http.ListenAndServe(":8080", mux)
}
