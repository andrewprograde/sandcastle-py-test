"""Command line interface for sandcastle."""

from __future__ import annotations

import argparse

FISH_ASCII_ART = "><(((('>"


def build_parser() -> argparse.ArgumentParser:
    """Build the sandcastle CLI argument parser."""
    parser = argparse.ArgumentParser(prog="sandcastle")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("fish", help="print a fish ASCII art")
    return parser


def main() -> None:
    """Run the sandcastle CLI."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "fish":
        print(FISH_ASCII_ART)


if __name__ == "__main__":
    main()
