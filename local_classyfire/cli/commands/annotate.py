from __future__ import annotations

import argparse

from ..annotators.mgf import annotate_mgf_file
from ..annotators.msp import annotate_msp_file


def add_annotate_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register annotate subcommand."""

    parser = subparsers.add_parser(
        "annotate",
        help="Annotate MSP/MGF files with ClassyFire classification metadata.",
        description=(
            "Read MSP/MGF files, find InChIKey or SMILES metadata lines, "
            "and insert ClassyFire classification lines after them."
        ),
    )

    format_subparsers = parser.add_subparsers(
        dest="file_type",
        required=True,
        help="Input file type.",
    )

    common_parser = build_common_annotate_parser()

    msp_parser = format_subparsers.add_parser(
        "msp",
        parents=[common_parser],
        help="Annotate MSP file.",
    )
    msp_parser.set_defaults(func=run_annotate_command)

    mgf_parser = format_subparsers.add_parser(
        "mgf",
        parents=[common_parser],
        help="Annotate MGF file.",
    )
    mgf_parser.set_defaults(func=run_annotate_command)


def build_common_annotate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input MSP/MGF file path.",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output annotated MSP/MGF file path.",
    )

    parser.add_argument(
        "--db",
        required=True,
        help="Path to LocalClassyFire SQLite database.",
    )

    parser.add_argument(
        "--identifier",
        choices=["inchikey", "smiles"],
        default="inchikey",
        help=(
            "Preferred identifier line to use. "
            "If missing, the other identifier type is also accepted."
        ),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help=(
            "Number of identifiers to classify in one batch. "
            "Default: 100."
        ),
    )

    parser.add_argument(
        "--style",
        choices=["auto", "colon", "equal"],
        default="auto",
        help=(
            "Classification line style. "
            "auto: MSP uses colon, MGF uses equal."
        ),
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
        help="Include ID columns during lookup. Currently not inserted into MSP/MGF.",
    )

    return parser


def run_annotate_command(args: argparse.Namespace) -> None:
    delimiter = resolve_delimiter(
        file_type=args.file_type,
        style=args.style,
    )

    if args.file_type == "msp":
        annotate_msp_file(
            input_path=args.input,
            output_path=args.output,
            db_path=args.db,
            identifier=args.identifier,
            batch_size=args.batch_size,
            timeout=args.timeout,
            request_interval_seconds=args.request_interval_seconds,
            retry_missing=args.retry_missing,
            include_ids=args.include_ids,
            delimiter=delimiter,
        )
        return

    if args.file_type == "mgf":
        annotate_mgf_file(
            input_path=args.input,
            output_path=args.output,
            db_path=args.db,
            identifier=args.identifier,
            batch_size=args.batch_size,
            timeout=args.timeout,
            request_interval_seconds=args.request_interval_seconds,
            retry_missing=args.retry_missing,
            include_ids=args.include_ids,
            delimiter=delimiter,
        )
        return

    raise ValueError(f"Unsupported file_type: {args.file_type}")


def resolve_delimiter(
    *,
    file_type: str,
    style: str,
) -> str:
    if style == "colon":
        return ":"

    if style == "equal":
        return "="

    if style != "auto":
        raise ValueError(f"Unsupported style: {style}")

    if file_type == "msp":
        return ":"

    if file_type == "mgf":
        return "="

    raise ValueError(f"Unsupported file_type: {file_type}")