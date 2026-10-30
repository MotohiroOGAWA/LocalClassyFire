from __future__ import annotations

import argparse
from pathlib import Path

from msentity import Dataset, load

from ..annotators.mgf import annotate_mgf_file
from ..annotators.msp import annotate_msp_file
from ..annotators.msdataset import annotate_msdataset


def add_annotate_command(
    subparsers: argparse._SubParsersAction,
) -> None:
    """Register annotate subcommand."""

    parser = subparsers.add_parser(
        "annotate",
        help="Annotate data with ClassyFire classification metadata.",
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

    msdataset_parser = format_subparsers.add_parser(
        "msdataset",
        aliases=["msds"],
        help="Annotate msentity.Dataset file.",
    )

    add_msdataset_arguments(msdataset_parser)
    msdataset_parser.set_defaults(func=run_annotate_command)

def add_identifier_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--identifier-type", "--identifier",
        dest="identifier_type",
        choices=["smiles", "inchikey"],
        default="inchikey",
        help="Identifier type. Default: inchikey. --identifier is a compatibility alias.",
    )
    parser.add_argument(
        "--identifier-column",
        help=(
            "Metadata column to read. Default: SMILES for smiles, InChIKey for inchikey. "
            "MSP/MGF match names ignoring case, spaces, underscores and hyphens; "
            "MSDS requires an exact column name. No fallback to another column."
        ),
    )


def resolve_identifier_column(args: argparse.Namespace) -> str:
    if args.identifier_column is not None:
        return args.identifier_column
    return "SMILES" if args.identifier_type == "smiles" else "InChIKey"


def add_msdataset_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        help="Input MSDataset file path.",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output annotated MSDataset file path.",
    )

    parser.add_argument(
        "--db",
        required=True,
        help="Path to LocalClassyFire SQLite database.",
    )

    add_identifier_arguments(parser)

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Number of identifiers to classify in one batch. Default: 100.",
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
        help="Include ID columns during lookup. Currently not added to dataset.",
    )

    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Do not overwrite existing classification columns.",
    )

    parser.add_argument(
        "--add-tag",
        action="store_true",
        help="Add the 'ClassyFire' tag to the output MSDataset.",
    )

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

    add_identifier_arguments(parser)

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

    parser.add_argument(
        "--add-tag",
        action="store_true",
        help="Add the 'ClassyFire' tag to the output MSDataset.",
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable tqdm progress bars.",
    )

    return parser


def run_annotate_command(args: argparse.Namespace) -> None:
    if args.file_type in {"msdataset", "msds"}:
        run_annotate_msdataset_command(args)
        return

    delimiter = resolve_delimiter(
        file_type=args.file_type,
        style=args.style,
    )

    if args.file_type == "msp":
        annotate_msp_file(
            input_path=args.input,
            output_path=args.output,
            db_path=args.db,
            identifier=args.identifier_type,
            identifier_column=resolve_identifier_column(args),
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
            identifier=args.identifier_type,
            identifier_column=resolve_identifier_column(args),
            batch_size=args.batch_size,
            timeout=args.timeout,
            request_interval_seconds=args.request_interval_seconds,
            retry_missing=args.retry_missing,
            include_ids=args.include_ids,
            delimiter=delimiter,
        )
        return

    raise ValueError(f"Unsupported file_type: {args.file_type}")

def run_annotate_msdataset_command(args: argparse.Namespace) -> None:
    with load(args.input) as dataset:
        annotated_dataset = annotate_msdataset(
            dataset=dataset,
            db_path=args.db,
            identifier_column=resolve_identifier_column(args),
            identifier_type=args.identifier_type,
            batch_size=args.batch_size,
            timeout=args.timeout,
            request_interval_seconds=args.request_interval_seconds,
            retry_missing=args.retry_missing,
            include_ids=args.include_ids,
            overwrite=not args.no_overwrite,
        )

        if args.add_tag:
            annotated_dataset.add_tag("ClassyFire")

        write_annotated_msdataset(
            dataset=annotated_dataset,
            output_path=args.output,
        )


def write_annotated_msdataset(
    *,
    dataset: Dataset,
    output_path: str,
    file_type: str | None = None,
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if file_type is None:
        suffix = path.suffix.lower()
        if suffix == ".msp":
            file_type = "msp"
        elif suffix == ".mgf":
            file_type = "mgf"
        elif suffix in [".msds", ".hdf5", ".h5"]:
            file_type = "msdataset"

    if file_type == "msdataset":
        # Keep the existing .h5/.hdf5 aliases, which produce an .msds file.
        path = path.with_suffix(".msds")
        file_type = "msds"

    if file_type not in {"msds", "msp", "mgf"}:
        raise ValueError(
            "Unsupported MSDataset output format. "
            "Supported output formats: .msds, .hdf5, .h5, .msp, .mgf"
        )

    dataset.save(path, format=file_type)


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