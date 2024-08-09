#!/usr/bin/python3.12

import getpass

print(
    f"""\
Content-Type: text/html

{getpass.getuser()}\
"""
)
