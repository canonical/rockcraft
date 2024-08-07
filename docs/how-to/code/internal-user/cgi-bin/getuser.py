#!/usr/bin/python3

import os

print(
    f"""\
Content-Type: text/html

{os.getlogin()}\
"""
)
