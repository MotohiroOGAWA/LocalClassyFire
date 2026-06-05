from __future__ import annotations

import time
from dataclasses import dataclass

from sqlalchemy.orm import Session

from local_classyfire.models import Classification
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