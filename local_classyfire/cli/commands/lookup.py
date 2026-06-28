from __future__ import annotations

import argparse

from local_classyfire.cli.io import collect_input_values
from local_classyfire.cli.lookup_runner import run_lookup
from local_classyfire.cli.output import write_dataframe


DEFAULT_DB_PATH = "db/classyfire_cache.sqlite"


def add_lookup_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register lookup subcommand."""

    parser = subparsers.add_parser(
        "lookup",
        help="Look up ClassyFire classification by SMILES or InChIKey.",
        description=(
            "Look up ClassyFire classification data from a single value "
            "or a newline-separated input file."
        ),
    )

    input_type_subparsers = parser.add_subparsers(
        dest="input_type",
        required=True,
        help="Input identifier type.",
    )

    common_parser = build_common_lookup_parser()

    _add_identifier_parser(
        input_type_subparsers,
        name="inchikey",
        help_text="Look up by InChIKey.",
        value_help="Single InChIKey value.",
        common_parser=common_parser,
    )

    _add_identifier_parser(
        input_type_subparsers,
        name="smiles",
        help_text="Look up by SMILES.",
        value_help="Single SMILES value.",
        common_parser=common_parser,
    )


def build_common_lookup_parser() -> argparse.ArgumentParser:
    """Build common options shared by lookup subcommands."""

    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "--db",
        default=DEFAULT_DB_PATH,
        help=(
            "Path to LocalClassyFire SQLite database. "
            f"Default: {DEFAULT_DB_PATH}."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output file path. If omitted, results are printed to stdout.",
    )

    parser.add_argument(
        "--format",
        choices=["tsv", "csv"],
        default="tsv",
        help="Output format. Default: tsv.",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="ClassyFire API request timeout in seconds.",
    )

    parser.add_argument(
        "--request-interval-seconds",
        type=float,
        default=5.0,
        help="Interval between ClassyFire API requests.",
    )

    parser.add_argument(
        "--retry-missing",
        action="store_true",
        help="Retry records already stored as missing queries.",
    )

    parser.add_argument(
        "--include-ids",
        action="store_true",
        help="Include database ID columns in the output.",
    )

    parser.add_argument(
        "--no-create-tables",
        action="store_true",
        help="Do not create missing database tables before lookup.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of identifiers to classify in one batch. Default: 100.",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable tqdm progress bars.",
    )

    return parser


def _add_identifier_parser(
    subparsers: argparse._SubParsersAction,
    *,
    name: str,
    help_text: str,
    value_help: str,
    common_parser: argparse.ArgumentParser,
) -> None:
    parser = subparsers.add_parser(
        name,
        parents=[common_parser],
        help=help_text,
    )

    parser.add_argument(
        "value",
        nargs="?",
        help=value_help,
    )

    parser.add_argument(
        "-i",
        "--input",
        default=None,
        help="Path to newline-separated input file.",
    )

    parser.set_defaults(func=run_lookup_command)


def run_lookup_command(args: argparse.Namespace) -> None:
    values = collect_input_values(
        value=args.value,
        input_path=args.input,
    )

    dataframe = run_lookup(
        db_path=args.db,
        input_type=args.input_type,
        values=values,
        batch_size=args.batch_size,
        timeout=args.timeout,
        request_interval_seconds=args.request_interval_seconds,
        retry_missing=args.retry_missing,
        include_ids=args.include_ids,
        create_missing_tables=not args.no_create_tables,
        show_progress=not args.no_progress,
    )

    write_dataframe(
        dataframe,
        output_path=args.output,
        output_format=args.format,
    )