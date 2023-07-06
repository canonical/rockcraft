#!/usr/bin/env python3

import argparse
from craft_cli.dispatcher import _CustomArgumentParser, Dispatcher
import os
import pathlib
from rockcraft import cli
import sys


def command_page_header(cmd, options_str, required_str):
    underline = "=" * len(cmd.name)
    return f"""
.. _ref_commands_{cmd.name}:

{cmd.name}
{underline}
{cmd.overview}

Usage
-----

:command:`rockcraft {cmd.name}{options_str}{required_str}`

"""


def make_sentence(t):
    return t[:1].upper() + t[1:].rstrip(".") + "."


def not_none(*args):
    return [x for x in args if x != None]


def make_section(title, items):
    s = ""
    if items:
        underline = "-" * len(title)
        s = f"{title}\n{underline}\n\n"

    for dest, (names, help_str) in sorted(items):
        names = " or ".join([f"``{name}``" for name in names])
        description = make_sentence(help_str)
        s += f"{names}\n   {description}\n"

    s += "\n"
    return s


def main(docs_dir):
    """Generate reference documentation for the command line interface,
    creating pages in the docs/reference/commands directory and creating the
    directory itself if necessary."""

    # Create the directory for the commands reference.
    commands_ref_dir = docs_dir / "reference" / "commands"
    if not commands_ref_dir.exists():
        commands_ref_dir.mkdir()

    # Create a dispatcher like Rockcraft does to get access to the same options.
    dispatcher = Dispatcher(
        "rockcraft",
        cli.COMMAND_GROUPS,
        summary="A tool to create OCI images",
        extra_global_args=cli.GLOBAL_ARGS,
        default_command=cli.commands.PackCommand,
    )

    help_builder = dispatcher._help_builder

    global_options = {}
    for arg in dispatcher.global_arguments:
        opts = not_none(arg.short_option, arg.long_option)
        global_options[arg.name] = (opts, arg.help_message)

    toc = []

    for group in cli.COMMAND_GROUPS:
        group_name = group.name.lower() + "-commands" + os.extsep + "rst"
        group_path = commands_ref_dir / group_name
        g = group_path.open("w")

        for cmd_class in sorted(group.commands, key=lambda c: c.name):
            cmd = cmd_class({})
            p = _CustomArgumentParser(help_builder)
            cmd.fill_parser(p)

            options = {}
            required = []
            options_str = " "

            for action in sorted(p._actions, key=lambda a: a.dest):
                if action.required:
                    required.append((action.dest, ([action.metavar], action.help)))
                elif action.option_strings and action.dest not in global_options:
                    options[action.dest] = (action.option_strings, action.help)

            cmd_path = commands_ref_dir / (cmd.name + os.extsep + "rst")

            if options or global_options:
                options_str += "[options]"
            required_str = "".join([(" <%s>" % vl[0]) for d, (vl, h) in required])

            f = cmd_path.open("w")
            f.write(command_page_header(cmd, options_str, required_str))
            f.write(make_section("Required", required))
            f.write(make_section("Options", options.items()))
            f.write(make_section("Global options", global_options.items()))

            # Add a section for the command to be included in the group reference.
            g.write(f":ref:`ref_commands_{cmd.name}`\n")
            g.write("   " + make_sentence(cmd.help_msg).replace("\n", "\n   ") + "\n\n")

            # Add an entry in the table of contents.
            toc.append(cmd.name)

    toc_path = commands_ref_dir / "toc.rst"
    f = toc_path.open("w")
    f.write(".. toctree::\n   :hidden:\n\n")
    for name in sorted(toc):
        f.write(f"   /reference/commands/{name}\n")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(pathlib.Path(sys.argv[1]))
