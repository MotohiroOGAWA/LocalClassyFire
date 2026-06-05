from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import ClassyFireQuery

from .classyfire_client import fetch_classyfire_result, ClassyFireNotFoundError, ClassyFireRequestError
from .classyfire_repository.query_writer import ClassyFireQueryWriter
from .classyfire_repository import ClassyFireRepository

def get_classyfire_query(
    session: Session,
    inchikey: str,
) -> ClassyFireQuery | None:
    """
    Get existing ClassyFireQuery by InChIKey.

    This function only checks the local database.
    It does not access classyfire.wishartlab.com.
    """
    return session.execute(
        select(ClassyFireQuery).where(
            ClassyFireQuery.inchikey == inchikey,
        )
    ).scalar_one_or_none()


def update_classyfire_by_inchikey(
    session: Session,
    inchikey: str,
    *,
    timeout: int = 30,
    retry_failed: bool = False,
) -> int | None:
    """
    Update local ClassyFire database by InChIKey.

    This function first checks ClassyFireQuery.
    If the InChIKey already exists in the local database, it does not access
    classyfire.wishartlab.com.

    Parameters
    ----------
    session:
        SQLAlchemy session.
    inchikey:
        Target InChIKey.
    timeout:
        Request timeout in seconds.
    retry_failed:
        If True, failed records are fetched again.

    Returns
    -------
    int | None
        classification_id if a classification exists.
        None if the record is known as not_found or error.
    """
    inchikey = inchikey.strip()

    query = get_classyfire_query(
        session=session,
        inchikey=inchikey,
    )

    if query is not None:
        if query.is_found:
            return query.classification_id

        if not query.is_found and not retry_failed:
            return None

    try:
        result = fetch_classyfire_result(
            inchikey=inchikey,
            timeout=timeout,
        )

    except ClassyFireNotFoundError as error:
        ClassyFireQueryWriter.mark_not_found(
            session=session,
            inchikey=inchikey,
            message=str(error),
        )
        return None

    except ClassyFireRequestError as error:
        ClassyFireQueryWriter.mark_error(
            session=session,
            inchikey=inchikey,
            message=str(error),
        )
        return None

    classification = ClassyFireRepository.upsert_result(
        session=session,
        result=result,
    )

    return classification.classification_id


if __name__ == "__main__":
    from .session import create_sqlite_engine, create_session_factory, create_tables
    import time

    engine = create_sqlite_engine(
        "db/classyfire_cache.sqlite",
        echo=True,
    )
    create_tables(engine)
    SessionFactory = create_session_factory(engine)


    with SessionFactory() as session:
        inchikey_list = [
            "AAABMNXUOFPYQK-WMBKCNCTSA-N",
            "BSYNRYMUTXBXSQ-UHFFFAOYSA-N",
            "AAABYGXUNQSIIU-UHFFFAOYSA-N",
            "AAAAURPNVGZDQV-UHFFFAOYSA-N",
            "AAAAWQOPBUPWEV-UHFFFAOYSA-N",
            "AAARPXDXUKJEIC-UHFFFAOYSA-N",
        ]
        for inchikey in inchikey_list:
            try:
                classification_id = update_classyfire_by_inchikey(
                    session=session,
                    inchikey=inchikey,
                    timeout=30,
                    retry_failed=False,
                )
                session.commit()

            except Exception:
                session.rollback()
                raise

            if classification_id is None:
                print(f"Skipped or not found: {inchikey}")
            else:
                print(f"Updated classification ID: {classification_id}")
            