from __future__ import annotations

import argparse

from .commands.lookup import add_lookup_command


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="local-classyfire",
        description="LocalClassyFire command line interface.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    add_lookup_command(subparsers)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as error:
        parser.exit(
            status=1,
            message=f"Error: {error}\n",
        )


if __name__ == "__main__":
    main()