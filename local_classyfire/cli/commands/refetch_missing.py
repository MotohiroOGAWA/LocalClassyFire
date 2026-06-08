from __future__ import annotations

import argparse

from local_classyfire.cli.missing_query_refetch_runner import (
    run_missing_query_refetch,
)
from local_classyfire.cli.output import write_dataframe


def add_refetch_missing_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register refetch-missing subcommand."""

    parser = subparsers.add_parser(
        "refetch-missing",
        help="Refetch ClassyFire missing queries ordered by UpdatedAt.",
        description=(
            "Refetch InChIKeys stored in ClassyFireMissingQuery. "
            "By default, all records are retried from oldest UpdatedAt."
        ),
    )

    parser.add_argument(
        "--db",
        required=True,
        help="Path to LocalClassyFire SQLite database.",
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
        "--limit",
        type=int,
        default=None,
        help="Maximum number of missing queries to refetch. Default: all.",
    )

    parser.add_argument(
        "--max-seconds",
        type=float,
        default=None,
        help="Maximum execution time in seconds. Default: no time limit.",
    )

    parser.add_argument(
        "--max-minutes",
        type=float,
        default=None,
        help="Maximum execution time in minutes. Default: no time limit.",
    )

    parser.add_argument(
        "--newest-first",
        action="store_true",
        help="Retry newer UpdatedAt records first. Default: oldest first.",
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
        "--include-ids",
        action="store_true",
        help="Include database ID columns in the output.",
    )

    parser.add_argument(
        "--no-create-tables",
        action="store_true",
        help="Do not create missing database tables before refetch.",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of identifiers to refetch in one batch. Default: 100.",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable tqdm progress bars.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show selected missing InChIKeys without refetching.",
    )

    parser.set_defaults(func=run_refetch_missing_command)


def run_refetch_missing_command(args: argparse.Namespace) -> None:
    max_seconds = args.max_seconds

    if args.max_minutes is not None:
        minutes_as_seconds = args.max_minutes * 60

        if max_seconds is None:
            max_seconds = minutes_as_seconds
        else:
            max_seconds = min(max_seconds, minutes_as_seconds)

    dataframe = run_missing_query_refetch(
        db_path=args.db,
        limit=args.limit,
        max_seconds=max_seconds,
        batch_size=args.batch_size,
        timeout=args.timeout,
        request_interval_seconds=args.request_interval_seconds,
        ascending=not args.newest_first,
        include_ids=args.include_ids,
        create_missing_tables=not args.no_create_tables,
        show_progress=not args.no_progress,
        dry_run=args.dry_run,
    )

    write_dataframe(
        dataframe,
        output_path=args.output,
        output_format=args.format,
    )