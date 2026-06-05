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
    Check local ClassyFireQuery records before accessing the ClassyFire API.

    is_found=True:
        The compound was found in the local cache.

    is_found=False:
        The compound was already queried but was not found, failed, skipped,
        or otherwise did not produce a classification.
        Details should be stored in ClassyFireQuery.message.
    """

    @classmethod
    def split_by_found_status(
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
            ClassyFireQuery.is_found,
        ).where(
            ClassyFireQuery.inchikey.in_(unique_keys)
        )

        rows = session.execute(statement).all()

        is_found_by_inchikey = {
            row.inchikey: row.is_found
            for row in rows
        }

        existing_success_set: set[str] = set()
        existing_failed_set: set[str] = set()
        keys_to_fetch: list[str] = []

        for inchikey in unique_keys:
            is_found = is_found_by_inchikey.get(inchikey)

            if is_found is True:
                existing_success_set.add(inchikey)
                continue

            if is_found is False:
                existing_failed_set.add(inchikey)

                if retry_failed:
                    keys_to_fetch.append(inchikey)

                continue

            # No ClassyFireQuery record exists.
            keys_to_fetch.append(inchikey)

        return CacheStatus(
            existing_success_set=existing_success_set,
            existing_failed_set=existing_failed_set,
            keys_to_fetch=keys_to_fetch,
        )

    @classmethod
    def split_by_query_status(
        cls,
        session: Session,
        inchikey_list: list[str],
        *,
        retry_failed: bool = False,
    ) -> CacheStatus:
        """
        Backward-compatible alias.

        Prefer split_by_found_status() in new code.
        """

        return cls.split_by_found_status(
            session=session,
            inchikey_list=inchikey_list,
            retry_failed=retry_failed,
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