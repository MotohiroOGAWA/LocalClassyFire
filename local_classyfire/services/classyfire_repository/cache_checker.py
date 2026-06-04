from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import ClassyFireQuery


@dataclass(frozen=True)
class CacheStatus:
    existing_success_set: set[str]
    existing_failed_set: set[str]
    keys_to_fetch: list[str]


class ClassyFireCacheChecker:
    """
    Check local ClassyFireQuery records before accessing ClassyFire API.
    """

    SUCCESS_STATUS = "success"
    FAILED_STATUSES = {"not_found", "error"}

    @classmethod
    def split_by_query_status(
        cls,
        session: Session,
        inchikey_list: list[str],
        *,
        retry_failed: bool = False,
    ) -> CacheStatus:
        unique_keys = cls._unique_valid_keys(inchikey_list)

        if not unique_keys:
            return CacheStatus(
                existing_success_set=set(),
                existing_failed_set=set(),
                keys_to_fetch=[],
            )

        statement = select(
            ClassyFireQuery.inchikey,
            ClassyFireQuery.query_status,
        ).where(
            ClassyFireQuery.inchikey.in_(unique_keys)
        )

        rows = session.execute(statement).all()

        status_by_inchikey = {
            row.inchikey: row.query_status
            for row in rows
        }

        existing_success_set: set[str] = set()
        existing_failed_set: set[str] = set()
        keys_to_fetch: list[str] = []

        for inchikey in unique_keys:
            status = status_by_inchikey.get(inchikey)

            if status == cls.SUCCESS_STATUS:
                existing_success_set.add(inchikey)
                continue

            if status in cls.FAILED_STATUSES:
                existing_failed_set.add(inchikey)

                if retry_failed:
                    keys_to_fetch.append(inchikey)

                continue

            # No ClassyFireQuery record exists, or status is unknown/pending.
            keys_to_fetch.append(inchikey)

        return CacheStatus(
            existing_success_set=existing_success_set,
            existing_failed_set=existing_failed_set,
            keys_to_fetch=keys_to_fetch,
        )

    @staticmethod
    def _unique_valid_keys(inchikey_list: list[str]) -> list[str]:
        return sorted(
            {
                inchikey.strip()
                for inchikey in inchikey_list
                if inchikey and inchikey.strip()
            }
        )