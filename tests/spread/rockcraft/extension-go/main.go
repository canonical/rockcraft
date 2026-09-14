package main

import (
	"fmt"
	"net/http"
	"os"
)

func hello(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintf(w, "ok")
}

func writeData(w http.ResponseWriter, req *http.Request) {
	filePath := "/app-dir/output.txt"
	data := []byte("Data written from Go app!\n")

	// Write data to the file with 0644 permissions
	err := os.WriteFile(filePath, data, 0644)
	if err != nil {
		// Return a 500 Internal Server Error if the write fails
		http.Error(w, fmt.Sprintf("Error writing file: %v", err), http.StatusInternalServerError)
		return
	}

	fmt.Fprintf(w, "written")
}

func main() {
	http.HandleFunc("/", hello)
	http.HandleFunc("/write-data", writeData) // Register the new endpoint

	fmt.Println("Server starting on :8000...")
	http.ListenAndServe(":8000", nil)
}
