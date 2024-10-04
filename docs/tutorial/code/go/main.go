package main

import (
	"fmt"
	"log"
	"net/http"
)

func helloWorldHandler(w http.ResponseWriter, req *http.Request) {
	log.Printf("new hello world request")
	fmt.Fprintf(w, "Hello, world!\n")
}

func main() {
	log.Printf("starting hello world application")
	http.HandleFunc("/", helloWorldHandler)
	http.ListenAndServe(":8000", nil)
}
