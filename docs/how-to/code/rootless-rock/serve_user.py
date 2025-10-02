#!/usr/bin/python3.12

import getpass

print(
    f"""\
Content-Type: text/html

Serving by {getpass.getuser()} on port 8080\
"""
)
