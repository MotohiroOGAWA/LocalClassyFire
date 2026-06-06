from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from local_classyfire.models import Classification
from local_classyfire.models import ClassyFireQuery
from local_classyfire.services.classyfire_client import fetch_classyfire_result
from local_classyfire.services.classyfire_result import ClassyFireResult

from .cache_checker import ClassyFireCacheChecker
from .classification_writer import ClassificationWriter
from .descriptor_writer import DescriptorWriter
from .node_writer import NodeWriter
from .query_writer import ClassyFireQueryWriter
from .term_writer import TermWriter


@dataclass(frozen=True)
class ClassyFireUpdateSummary:
    total_count: int
    existing_success_count: int
    existing_failed_count: int
    api_request_count: int
    success_count: int
    failed_count: int


class ClassyFireRepository:
    """
    Main repository for ClassyFire data.

    This class avoids unnecessary access to classyfire.wishartlab.com.
    Existing successful and failed query statuses are reused from ClassyFireQuery.
    """

    @classmethod
    def upsert_result(
        cls,
        session: Session,
        result: ClassyFireResult,
    ) -> Classification:
        """
        Store one parsed ClassyFire result.
        This method does not call ClassyFire API.
        """
        classification = ClassificationWriter.upsert_classification(
            session=session,
            result=result,
        )

        NodeWriter.upsert_classification_nodes_from_result(
            session=session,
            result=result,
        )

        NodeWriter.replace_all_nodes(
            session=session,
            classification=classification,
            intermediate_nodes=result.intermediate_nodes,
            alternative_parents=result.alternative_parents,
            ancestors=result.ancestors,
        )

        DescriptorWriter.replace_external_descriptors(
            session=session,
            classification=classification,
            descriptors=result.external_descriptors,
        )

        TermWriter.replace_all_terms(
            session=session,
            classification=classification,
            substituents=result.substituents,
            predicted_chebi_terms=result.predicted_chebi_terms,
            predicted_lipidmaps_terms=result.predicted_lipidmaps_terms,
        )

        ClassyFireQueryWriter.mark_success(
            session=session,
            inchikey=result.inchikey,
            classification=classification,
            smiles=result.smiles,
        )

        session.flush()

        return classification

    @classmethod
    def update_missing_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
        *,
        skip_missing: bool = False,
        retry_failed: bool = False,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        commit_each: bool = True,
    ) -> ClassyFireUpdateSummary:
        """
        Fetch only InChIKeys that are not already recorded in ClassyFireQuery.

        Parameters
        ----------
        skip_missing:
            True means do not call ClassyFire API at all.
            Only local DB records are used.

        retry_failed:
            False means InChIKeys with is_found=False are not fetched again.
        """
        unique_keys = sorted(
            {
                inchikey.strip()
                for inchikey in inchikey_list
                if inchikey and inchikey.strip()
            }
        )

        cache_status = ClassyFireCacheChecker.split_by_found_status(
            session=session,
            inchikey_list=unique_keys,
            retry_failed=retry_failed,
        )

        keys_to_fetch = cache_status.keys_to_fetch

        if skip_missing:
            return ClassyFireUpdateSummary(
                total_count=len(unique_keys),
                existing_success_count=len(cache_status.existing_success_set),
                existing_failed_count=len(cache_status.existing_failed_set),
                api_request_count=0,
                success_count=0,
                failed_count=0,
            )

        success_count = 0
        failed_count = 0
        last_request_time = 0.0

        for inchikey in keys_to_fetch:
            try:
                current_time = time.time()
                elapsed = current_time - last_request_time

                if elapsed < request_interval_seconds:
                    time.sleep(request_interval_seconds - elapsed)

                result = fetch_classyfire_result(
                    inchikey=inchikey,
                    timeout=timeout,
                )

                last_request_time = time.time()

                cls.upsert_result(
                    session=session,
                    result=result,
                )

                success_count += 1

                if commit_each:
                    session.commit()

            except ValueError as error:
                failed_count += 1

                ClassyFireQueryWriter.mark_not_found(
                    session=session,
                    inchikey=inchikey,
                    message=str(error),
                )

                if commit_each:
                    session.commit()

            except Exception as error:
                failed_count += 1

                ClassyFireQueryWriter.mark_error(
                    session=session,
                    inchikey=inchikey,
                    message=str(error),
                )

                if commit_each:
                    session.commit()

        if not commit_each:
            session.commit()

        return ClassyFireUpdateSummary(
            total_count=len(unique_keys),
            existing_success_count=len(cache_status.existing_success_set),
            existing_failed_count=len(cache_status.existing_failed_set),
            api_request_count=len(keys_to_fetch),
            success_count=success_count,
            failed_count=failed_count,
        )

    @staticmethod
    def _normalize_inchikey(inchikey: str) -> str:
        """Normalize an InChIKey for lookup."""
        return inchikey.strip()

    @classmethod
    def get_query_by_inchikey(
        cls,
        session: Session,
        inchikey: str,
    ) -> ClassyFireQuery | None:
        """
        Get one ClassyFireQuery by InChIKey.

        This method does not call ClassyFire API.
        If the query is not stored in the local DB, returns None.
        """
        normalized_inchikey = cls._normalize_inchikey(inchikey)

        if not normalized_inchikey:
            return None

        stmt = (
            select(ClassyFireQuery)
            .where(ClassyFireQuery.inchikey == normalized_inchikey)
        )

        return session.execute(stmt).scalar_one_or_none()

    @classmethod
    def get_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
    ) -> dict[str, ClassyFireQuery | None]:
        """
        Get ClassyFireQuery records by InChIKey list.

        This method does not call ClassyFire API.
        Missing InChIKeys are returned with None.
        """
        normalized_keys = [
            cls._normalize_inchikey(inchikey)
            for inchikey in inchikey_list
            if inchikey and cls._normalize_inchikey(inchikey)
        ]

        unique_keys = sorted(set(normalized_keys))

        if not unique_keys:
            return {}

        stmt = (
            select(ClassyFireQuery)
            .where(ClassyFireQuery.inchikey.in_(unique_keys))
        )

        query_records = session.execute(stmt).scalars().all()

        query_by_inchikey = {
            query.inchikey: query
            for query in query_records
        }

        return {
            inchikey: query_by_inchikey.get(inchikey)
            for inchikey in unique_keys
        }

    @classmethod
    def get_or_fetch_query_by_inchikey(
        cls,
        session: Session,
        inchikey: str,
        *,
        timeout: int = 30,
        commit: bool = True,
    ) -> ClassyFireQuery | None:
        """
        Get one ClassyFireQuery by InChIKey.

        If it does not exist locally, fetch ClassyFireResult from ClassyFire API,
        upsert it, and then get ClassyFireQuery again.

        If ClassyFire cannot return a result, the failure status is stored in
        ClassyFireQuery and then returned if it was successfully recorded.
        """
        normalized_inchikey = cls._normalize_inchikey(inchikey)

        if not normalized_inchikey:
            return None

        existing_query = cls.get_query_by_inchikey(
            session=session,
            inchikey=normalized_inchikey,
        )

        if existing_query is not None:
            return existing_query

        try:
            result = fetch_classyfire_result(
                inchikey=normalized_inchikey,
                timeout=timeout,
            )

            cls.upsert_result(
                session=session,
                result=result,
            )

            if commit:
                session.commit()

        except ValueError as error:
            ClassyFireQueryWriter.mark_not_found(
                session=session,
                inchikey=normalized_inchikey,
                message=str(error),
            )

            if commit:
                session.commit()

        except Exception as error:
            ClassyFireQueryWriter.mark_error(
                session=session,
                inchikey=normalized_inchikey,
                message=str(error),
            )

            if commit:
                session.commit()

        return cls.get_query_by_inchikey(
            session=session,
            inchikey=normalized_inchikey,
        )

    @classmethod
    def get_or_fetch_queries_by_inchikey_list(
        cls,
        session: Session,
        inchikey_list: list[str],
        *,
        timeout: int = 30,
        request_interval_seconds: float = 5.0,
        commit_each: bool = True,
    ) -> dict[str, ClassyFireQuery | None]:
        """
        Get ClassyFireQuery records by InChIKey list.

        Existing records are returned from the local DB.
        Missing records are fetched from ClassyFire API, upserted, and then
        queried again.

        Returns
        -------
        dict[str, ClassyFireQuery | None]
            Mapping from normalized InChIKey to ClassyFireQuery.
            If even failure recording failed, the value can remain None.
        """
        normalized_keys = [
            cls._normalize_inchikey(inchikey)
            for inchikey in inchikey_list
            if inchikey and cls._normalize_inchikey(inchikey)
        ]

        unique_keys = sorted(set(normalized_keys))

        if not unique_keys:
            return {}

        existing_queries = cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_keys,
        )

        missing_keys = [
            inchikey
            for inchikey, query in existing_queries.items()
            if query is None
        ]

        last_request_time = 0.0

        for inchikey in missing_keys:
            try:
                current_time = time.time()
                elapsed = current_time - last_request_time

                if elapsed < request_interval_seconds:
                    time.sleep(request_interval_seconds - elapsed)

                result = fetch_classyfire_result(
                    inchikey=inchikey,
                    timeout=timeout,
                )

                last_request_time = time.time()

                cls.upsert_result(
                    session=session,
                    result=result,
                )

                if commit_each:
                    session.commit()

            except ValueError as error:
                ClassyFireQueryWriter.mark_not_found(
                    session=session,
                    inchikey=inchikey,
                    message=str(error),
                )

                if commit_each:
                    session.commit()

            except Exception as error:
                ClassyFireQueryWriter.mark_error(
                    session=session,
                    inchikey=inchikey,
                    message=str(error),
                )

                if commit_each:
                    session.commit()

        if not commit_each:
            session.commit()

        return cls.get_queries_by_inchikey_list(
            session=session,
            inchikey_list=unique_keys,
        )