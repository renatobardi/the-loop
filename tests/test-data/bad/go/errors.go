package main

import (
	"net/http"
	"os"
)

// BAD: go-error-001 — error ignored with blank identifier
// ruleid: go-error-001
func readFile(filename string) []byte {
	f, _ := os.Open(filename)
	defer f.Close()
	data := make([]byte, 1024)
	f.Read(data)
	return data
}

// ruleid: go-error-001
func createFile(path string) *os.File {
	f, _ := os.Create(path)
	return f
}

// ruleid: go-error-001
func queryDB(db *sql.DB, query string) *sql.Rows {
	rows, _ := db.Query(query)
	return rows
}

// BAD: go-error-002 — panic in HTTP handler
// ruleid: go-error-002
func handler(w http.ResponseWriter, r *http.Request) {
	panic("unimplemented endpoint")
}

// ruleid: go-error-002
func userHandler(w http.ResponseWriter, r *http.Request) {
	data := loadData()
	if data == nil {
		panic("failed to load data")
	}
	fmt.Fprintln(w, data)
}
