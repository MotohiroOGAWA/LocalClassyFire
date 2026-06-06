from __future__ import annotations

from dataclasses import dataclass
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import ClassyFireMissingQuery, ClassyFireQuery
from .classyfire_repository import ClassyFireRepository
from .classyfire_client import (
    ClassyFireNotFoundError,
    ClassyFireRequestError,
    fetch_classyfire_result,
)
from .classyfire_result import ClassyFireResult

ClassyFireCachedQuery = ClassyFireQuery | ClassyFireMissingQuery


@dataclass(frozen=True)
class ClassyFireCacheStatus:
    """Cache status for a list of InChIKeys."""

    cached_query_by_inchikey: dict[str, ClassyFireCachedQuery]
    uncached_inchikeys: list[str]


class ClassyFireQueryRepository:
    """Repository for successful and missing ClassyFire query records.

    ClassyFireQuery stores only successful ClassyFire results.
    ClassyFireMissingQuery stores missing, failed, or invalid query records.
    """

    @staticmethod
    def normalize_inchikey(
        inchikey: str | None,
    ) -> str | None:
        if inchikey is None:
            return None

        normalized = inchikey.strip()

        if not normalized:
            return None

        return normalized

    @classmethod
    def normalize_inchikeys(
        cls,
        inchikey_list: list[str],
    ) -> list[str]:
        return sorted(
            {
                normalized
                for inchikey in inchikey_list
                if (normalized := cls.normalize_inchikey(inchikey)) is not None
            }
        )

    # ------------------------------------------------------------------
    # Public read methods
    # ------------------------------------------------------------------

    @classmethod
    def get_query_by_inchikey(
        cls,
        session: Session,
        inchikey: str | None,
    ) -> ClassyFireCachedQuery | None:
        """Get cached ClassyFire query by InChIKey.

        Lookup order:
        1. ClassyFireQuery
        2. ClassyFireMissingQuery
        3. None
        """
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            return None

        success_query = cls._get_success_query_by_inchikey(
            session=session,
            inchikey=normalized,
        )

        if success_query is not None:
            return success_query

        return cls._get_missing_query_by_inchikey(
            session=session,
            inchikey=normalized,
        )

    @classmethod
    def get_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
    ) -> dict[str, ClassyFireCachedQuery | None]:
        """Get cached records by InChIKey list.

        This method searches ClassyFireQuery first.
        Then it searches ClassyFireMissingQuery only for InChIKeys that were
        not found in ClassyFireQuery.
        """
        unique_inchikeys = cls.normalize_inchikeys(inchikey_list)

        if not unique_inchikeys:
            return {}

        success_by_inchikey = cls._get_success_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_inchikeys,
        )

        result: dict[str, ClassyFireCachedQuery | None] = {
            inchikey: success_by_inchikey.get(inchikey)
            for inchikey in unique_inchikeys
        }

        missing_lookup_inchikeys = [
            inchikey
            for inchikey in unique_inchikeys
            if result[inchikey] is None
        ]

        if missing_lookup_inchikeys:
            missing_by_inchikey = cls._get_missing_queries_by_inchikey_list(
                session=session,
                inchikey_list=missing_lookup_inchikeys,
            )

            for inchikey in missing_lookup_inchikeys:
                result[inchikey] = missing_by_inchikey.get(inchikey)

        return result

    @classmethod
    def split_inchikeys_by_cache_status(
        cls,
        session: Session,
        inchikey_list: list[str],
    ) -> ClassyFireCacheStatus:
        """Split InChIKeys into cached and uncached."""
        unique_inchikeys = cls.normalize_inchikeys(inchikey_list)

        if not unique_inchikeys:
            return ClassyFireCacheStatus(
                cached_query_by_inchikey={},
                uncached_inchikeys=[],
            )

        query_by_inchikey = cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_inchikeys,
        )

        cached_query_by_inchikey = {
            inchikey: query
            for inchikey, query in query_by_inchikey.items()
            if query is not None
        }

        uncached_inchikeys = [
            inchikey
            for inchikey in unique_inchikeys
            if query_by_inchikey.get(inchikey) is None
        ]

        return ClassyFireCacheStatus(
            cached_query_by_inchikey=cached_query_by_inchikey,
            uncached_inchikeys=uncached_inchikeys,
        )

    @classmethod
    def get_or_create_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
        *,
        results: list[ClassyFireResult] | None = None,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        retry_missing: bool = False,
        replace_missing_with_result: bool = True,
        flush: bool = True,
    ) -> dict[str, ClassyFireCachedQuery | None]:
        """Get or create cached ClassyFire query records.

        Parameters
        ----------
        inchikey_list:
            InChIKeys to get or fetch. If results is None, this is used to
            fetch ClassyFire API results.

        results:
            Parsed ClassyFireResult objects. If provided, these are used directly
            without API access.

        retry_missing:
            If False, cached ClassyFireMissingQuery records are returned as-is.
            If True, missing records are fetched again from ClassyFire API.

        replace_missing_with_result:
            If True, when a successful result is available for an InChIKey that
            already has a missing record, the missing record is deleted and a
            successful ClassyFireQuery is created.
        """
        result_by_inchikey = cls._normalize_result_list(results or [])

        input_inchikeys = set(result_by_inchikey)

        if inchikey_list is not None:
            input_inchikeys.update(cls.normalize_inchikeys(inchikey_list))

        unique_inchikeys = sorted(input_inchikeys)

        if not unique_inchikeys:
            return {}

        cached_by_inchikey = cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_inchikeys,
        )

        results_to_create: list[ClassyFireResult] = []
        output_by_inchikey: dict[str, ClassyFireCachedQuery | None] = dict(
            cached_by_inchikey
        )

        last_request_time = 0.0

        for inchikey in unique_inchikeys:
            cached_query = cached_by_inchikey.get(inchikey)
            supplied_result = result_by_inchikey.get(inchikey)

            if supplied_result is not None:
                if isinstance(cached_query, ClassyFireQuery):
                    continue

                if (
                    isinstance(cached_query, ClassyFireMissingQuery)
                    and replace_missing_with_result
                ):
                    cls._delete_missing_query(
                        session=session,
                        inchikey=inchikey,
                        flush=False,
                    )
                    output_by_inchikey[inchikey] = None

                results_to_create.append(supplied_result)
                continue

            if isinstance(cached_query, ClassyFireQuery):
                continue

            if isinstance(cached_query, ClassyFireMissingQuery) and not retry_missing:
                continue

            try:
                if request_interval_seconds > 0:
                    current_time = time.time()
                    elapsed = current_time - last_request_time

                    if elapsed < request_interval_seconds:
                        time.sleep(request_interval_seconds - elapsed)

                fetched_result = fetch_classyfire_result(
                    inchikey=inchikey,
                    timeout=timeout,
                )

                last_request_time = time.time()

                if isinstance(cached_query, ClassyFireMissingQuery):
                    cls._delete_missing_query(
                        session=session,
                        inchikey=inchikey,
                        flush=False,
                    )
                    output_by_inchikey[inchikey] = None

                results_to_create.append(fetched_result)

            except ClassyFireNotFoundError as error:
                missing_query = cls._get_or_create_missing_query(
                    session=session,
                    inchikey=inchikey,
                    reason="not_found",
                    message=str(error),
                    flush=False,
                )
                output_by_inchikey[inchikey] = missing_query

            except ClassyFireRequestError as error:
                missing_query = cls._get_or_create_missing_query(
                    session=session,
                    inchikey=inchikey,
                    reason="request_error",
                    message=str(error),
                    flush=False,
                )
                output_by_inchikey[inchikey] = missing_query

            except Exception as error:
                missing_query = cls._get_or_create_missing_query(
                    session=session,
                    inchikey=inchikey,
                    reason="unknown_error",
                    message=str(error),
                    flush=False,
                )
                output_by_inchikey[inchikey] = missing_query

        if results_to_create:
            resolved_results = ClassyFireRepository.resolve_results(
                session=session,
                results=results_to_create,
                flush=False,
            )

            resolved_by_inchikey = {
                resolved.inchikey: resolved
                for resolved in resolved_results
            }

            existing_by_inchikey = cls.get_queries_by_inchikey_list(
                session=session,
                inchikey_list=list(resolved_by_inchikey),
            )

            queries_to_add: list[ClassyFireQuery] = []

            for inchikey, resolved in resolved_by_inchikey.items():
                existing = existing_by_inchikey.get(inchikey)

                if existing is not None:
                    output_by_inchikey[inchikey] = existing
                    continue

                query = ClassyFireQuery(
                    inchikey=resolved.inchikey,
                    smiles=resolved.smiles,
                    kingdom_id=resolved.kingdom_id,
                    superclass_id=resolved.superclass_id,
                    class_id=resolved.class_id,
                    subclass_id=resolved.subclass_id,
                    direct_parent_id=resolved.direct_parent_id,
                    intermediate_node_set_id=resolved.intermediate_node_set_id,
                    alternative_parent_set_id=resolved.alternative_parent_set_id,
                    ancestor_set_id=resolved.ancestor_set_id,
                    molecular_framework_id=resolved.molecular_framework_id,
                    substituent_set_id=resolved.substituent_set_id,
                    external_descriptor_set_id=resolved.external_descriptor_set_id,
                    predicted_chebi_term_set_id=(
                        resolved.predicted_chebi_term_set_id
                    ),
                    predicted_lipidmaps_term_set_id=(
                        resolved.predicted_lipidmaps_term_set_id
                    ),
                    description=resolved.description,
                    classification_version=resolved.classification_version,
                )

                queries_to_add.append(query)
                output_by_inchikey[inchikey] = query

            if queries_to_add:
                session.add_all(queries_to_add)

        if flush:
            session.flush()
            session.commit()

        return cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_inchikeys,
        )

    # ------------------------------------------------------------------
    # Private success read methods
    # ------------------------------------------------------------------

    @classmethod
    def _get_success_query_by_inchikey(
        cls,
        session: Session,
        inchikey: str | None,
    ) -> ClassyFireQuery | None:
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            return None

        stmt = (
            select(ClassyFireQuery)
            .where(ClassyFireQuery.inchikey == normalized)
        )

        return session.execute(stmt).scalar_one_or_none()

    @classmethod
    def _get_success_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
    ) -> dict[str, ClassyFireQuery]:
        unique_inchikeys = cls.normalize_inchikeys(inchikey_list)

        if not unique_inchikeys:
            return {}

        stmt = (
            select(ClassyFireQuery)
            .where(ClassyFireQuery.inchikey.in_(unique_inchikeys))
        )

        records = session.execute(stmt).scalars().all()

        return {
            record.inchikey: record
            for record in records
        }

    # ------------------------------------------------------------------
    # Private missing read methods
    # ------------------------------------------------------------------

    @classmethod
    def _get_missing_query_by_inchikey(
        cls,
        session: Session,
        inchikey: str | None,
    ) -> ClassyFireMissingQuery | None:
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            return None

        stmt = (
            select(ClassyFireMissingQuery)
            .where(ClassyFireMissingQuery.inchikey == normalized)
        )

        return session.execute(stmt).scalar_one_or_none()

    @classmethod
    def _get_missing_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
    ) -> dict[str, ClassyFireMissingQuery]:
        unique_inchikeys = cls.normalize_inchikeys(inchikey_list)

        if not unique_inchikeys:
            return {}

        stmt = (
            select(ClassyFireMissingQuery)
            .where(ClassyFireMissingQuery.inchikey.in_(unique_inchikeys))
        )

        records = session.execute(stmt).scalars().all()

        return {
            record.inchikey: record
            for record in records
        }

    # ------------------------------------------------------------------
    # Private create methods
    # ------------------------------------------------------------------

    @classmethod
    def _create_success_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        smiles: str | None = None,
        kingdom_id: int | None = None,
        superclass_id: int | None = None,
        class_id: int | None = None,
        subclass_id: int | None = None,
        direct_parent_id: int | None = None,
        intermediate_node_set_id: int | None = None,
        alternative_parent_set_id: int | None = None,
        ancestor_set_id: int | None = None,
        molecular_framework_id: int | None = None,
        substituent_set_id: int | None = None,
        external_descriptor_set_id: int | None = None,
        predicted_chebi_term_set_id: int | None = None,
        predicted_lipidmaps_term_set_id: int | None = None,
        description: str | None = None,
        classification_version: str | None = None,
        flush: bool = True,
    ) -> ClassyFireQuery:
        """Create one successful ClassyFireQuery.

        This is private because the caller must resolve all foreign key IDs
        before creating a successful query record.
        """
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            raise ValueError("InChIKey is required to create ClassyFireQuery.")

        query = ClassyFireQuery(
            inchikey=normalized,
            smiles=smiles,
            kingdom_id=kingdom_id,
            superclass_id=superclass_id,
            class_id=class_id,
            subclass_id=subclass_id,
            direct_parent_id=direct_parent_id,
            intermediate_node_set_id=intermediate_node_set_id,
            alternative_parent_set_id=alternative_parent_set_id,
            ancestor_set_id=ancestor_set_id,
            molecular_framework_id=molecular_framework_id,
            substituent_set_id=substituent_set_id,
            external_descriptor_set_id=external_descriptor_set_id,
            predicted_chebi_term_set_id=predicted_chebi_term_set_id,
            predicted_lipidmaps_term_set_id=predicted_lipidmaps_term_set_id,
            description=description,
            classification_version=classification_version,
        )

        session.add(query)

        if flush:
            session.flush()

        return query

    @classmethod
    def _create_missing_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        reason: str | None = None,
        message: str | None = None,
        flush: bool = True,
    ) -> ClassyFireMissingQuery:
        """Create one missing/failed ClassyFire query record."""
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            raise ValueError(
                "InChIKey is required to create ClassyFireMissingQuery."
            )

        missing_query = ClassyFireMissingQuery(
            inchikey=normalized,
            reason=reason,
            message=message,
        )

        session.add(missing_query)

        if flush:
            session.flush()

        return missing_query

    # ------------------------------------------------------------------
    # Private get-or-create methods
    # ------------------------------------------------------------------

    @classmethod
    def _get_or_create_success_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        smiles: str | None = None,
        kingdom_id: int | None = None,
        superclass_id: int | None = None,
        class_id: int | None = None,
        subclass_id: int | None = None,
        direct_parent_id: int | None = None,
        intermediate_node_set_id: int | None = None,
        alternative_parent_set_id: int | None = None,
        ancestor_set_id: int | None = None,
        molecular_framework_id: int | None = None,
        substituent_set_id: int | None = None,
        external_descriptor_set_id: int | None = None,
        predicted_chebi_term_set_id: int | None = None,
        predicted_lipidmaps_term_set_id: int | None = None,
        description: str | None = None,
        classification_version: str | None = None,
        flush: bool = True,
    ) -> ClassyFireCachedQuery:
        """Get cached record or create successful query.

        If either successful or missing record already exists, return it.
        """
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            raise ValueError("InChIKey is required.")

        existing = cls.get_query_by_inchikey(
            session=session,
            inchikey=normalized,
        )

        if existing is not None:
            return existing

        return cls._create_success_query(
            session=session,
            inchikey=normalized,
            smiles=smiles,
            kingdom_id=kingdom_id,
            superclass_id=superclass_id,
            class_id=class_id,
            subclass_id=subclass_id,
            direct_parent_id=direct_parent_id,
            intermediate_node_set_id=intermediate_node_set_id,
            alternative_parent_set_id=alternative_parent_set_id,
            ancestor_set_id=ancestor_set_id,
            molecular_framework_id=molecular_framework_id,
            substituent_set_id=substituent_set_id,
            external_descriptor_set_id=external_descriptor_set_id,
            predicted_chebi_term_set_id=predicted_chebi_term_set_id,
            predicted_lipidmaps_term_set_id=predicted_lipidmaps_term_set_id,
            description=description,
            classification_version=classification_version,
            flush=flush,
        )

    @classmethod
    def _get_or_create_missing_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        reason: str | None = None,
        message: str | None = None,
        flush: bool = True,
    ) -> ClassyFireCachedQuery:
        """Get cached record or create missing query.

        If either successful or missing record already exists, return it.
        """
        normalized = cls.normalize_inchikey(inchikey)

        if normalized is None:
            raise ValueError("InChIKey is required.")

        existing = cls.get_query_by_inchikey(
            session=session,
            inchikey=normalized,
        )

        if existing is not None:
            return existing

        return cls._create_missing_query(
            session=session,
            inchikey=normalized,
            reason=reason,
            message=message,
            flush=flush,
        )

    @classmethod
    def _normalize_result_list(
        cls,
        results: list[ClassyFireResult],
    ) -> dict[str, ClassyFireResult]:
        result_by_inchikey: dict[str, ClassyFireResult] = {}

        for result in results:
            inchikey = cls.normalize_inchikey(result.inchikey)

            if inchikey is None:
                continue

            result_by_inchikey.setdefault(inchikey, result)

        return result_by_inchikey


    @classmethod
    def _delete_missing_query(
        cls,
        session: Session,
        *,
        inchikey: str,
        flush: bool = True,
    ) -> None:
        missing_query = cls._get_missing_query_by_inchikey(
            session=session,
            inchikey=inchikey,
        )

        if missing_query is None:
            return

        session.delete(missing_query)

        if flush:
            session.flush()