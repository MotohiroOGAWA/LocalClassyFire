from __future__ import annotations

import argparse
from pathlib import Path

from local_classyfire.services.session import (
    create_session_factory,
    create_sqlite_engine,
    create_tables,
)
from local_classyfire.services.update_by_inchikey import (
    update_classyfire_by_inchikey,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Update local ClassyFire database by InChIKey.",
    )

    parser.add_argument(
        "inchikey",
        type=str,
        help="Target InChIKey.",
    )

    parser.add_argument(
        "--db",
        type=Path,
        default=Path("db/classyfire_cache.sqlite"),
        help="SQLite database path.",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="ClassyFire API timeout in seconds.",
    )

    parser.add_argument(
        "--echo",
        action="store_true",
        help="Show SQL logs.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    engine = create_sqlite_engine(
        sqlite_path=args.db,
        echo=args.echo,
    )

    create_tables(engine)

    SessionFactory = create_session_factory(engine)

    with SessionFactory() as session:
        try:
            classification_id = update_classyfire_by_inchikey(
                session=session,
                inchikey=args.inchikey,
                timeout=args.timeout,
            )
            session.commit()

        except Exception:
            session.rollback()
            raise

    print(f"Updated ClassificationID={classification_id}")


if __name__ == "__main__":
    main()