package main

import (
	"fmt"
	"log"
	"net/http"
)

func helloWorld(w http.ResponseWriter, req *http.Request) {
	log.Printf("new hello world request")
	fmt.Fprintf(w, "Hello World")
}

func main() {
	log.Printf("starting hello world application")
	http.HandleFunc("/", helloWorld)
	http.ListenAndServe(":8000", nil)
}
