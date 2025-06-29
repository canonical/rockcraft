"""A tool for updating Ubuntu release dates from Launchpad."""

import argparse
import csv
import json
import pathlib

import httpx

UBUNTU_INFO_URL = (
    "https://git.launchpad.net/ubuntu/+source/distro-info-data/plain/ubuntu.csv"
)


def get_csv_from_launchpad(url: str = UBUNTU_INFO_URL) -> csv.DictReader:
    """Get a CSV from the internet."""
    response = httpx.get(url)
    response.raise_for_status()
    return csv.DictReader(response.text)


def get_csv_from_local(
    path: pathlib.Path = pathlib.Path("/usr/share/distro-info/ubuntu.csv"),
):
    """Use a local file to get the Ubuntu CSV."""
    return csv.DictReader(path.open())


def parse_ubuntu_info(values: csv.DictReader) -> dict[str, dict[str, str]]:
    """Parse an ubuntu distro-info csv to a dict."""
    return {
        row["version"].removesuffix(" LTS"): {
            "release": row["release"],
            "eol": row["eol-server"] or row["eol"],
            "eol-esm": row["eol-esm"] or row["eol-server"] or row["eol"],
        }
        for row in values
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    parser.add_argument(
        "--dest",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parents[1] / "rockcraft/data/ubuntu.json",
    )
    args = parser.parse_args()

    data = get_csv_from_local() if args.local else get_csv_from_launchpad()
    parsed_data = parse_ubuntu_info(data)
    with args.dest.open("w") as output:
        json.dump(parsed_data, output, indent=2)


if __name__ == "__main__":
    main()
