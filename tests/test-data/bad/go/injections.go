package main

import (
	"fmt"
	"net/http"
	"os/exec"
	"path/filepath"
)

// BAD: go-injection-001 — fmt.Sprintf in SQL query
// ruleid: go-injection-001
func getUserByID(db *sql.DB, id string) {
	db.Query(fmt.Sprintf("SELECT * FROM users WHERE id = %s", id))
}

// ruleid: go-injection-001
func deleteRecord(db *sql.DB, table, id string) {
	db.Exec(fmt.Sprintf("DELETE FROM %s WHERE id = '%s'", table, id))
}

// BAD: go-injection-002 — exec.Command with user input
// ruleid: go-injection-002
func runCommand(userInput string) {
	exec.Command("sh", "-c", userInput).Run()
}

// BAD: go-injection-003 — filepath.Join with request input
// ruleid: go-injection-003
func serveFile(w http.ResponseWriter, r *http.Request) {
	filePath := filepath.Join("/data", r.PathValue("file"))
	http.ServeFile(w, r, filePath)
}
