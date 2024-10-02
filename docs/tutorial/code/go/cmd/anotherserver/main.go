package main

import (
	"fmt"
	"log"
	"net/http"
)

func helloWorld(w http.ResponseWriter, req *http.Request) {
	log.Printf("anotherserver hello world request")
	fmt.Fprintf(w, "Hello World from anotherserver")
}

func main() {
	log.Printf("starting anotherserver hello world application")
	http.HandleFunc("/", helloWorld)
	http.ListenAndServe(":8000", nil)
}
