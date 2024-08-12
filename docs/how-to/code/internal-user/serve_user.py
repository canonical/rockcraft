#!/usr/bin/python3.12

import getpass
import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving by {getpass.getuser()} on port {PORT}")
    httpd.serve_forever()
