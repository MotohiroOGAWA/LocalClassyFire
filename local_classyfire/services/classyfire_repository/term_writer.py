from __future__ import annotations

from sqlalchemy.orm import Session

from local_classyfire.models import (
    Classification,
    ClassificationPredictedChebiTerm,
    ClassificationPredictedLipidmapsTerm,
    ClassificationSubstituent,
    PredictedChebiTerm,
    PredictedLipidmapsTerm,
    Substituent,
)

from .utils import get_or_create, replace_relationship_items


class TermWriter:
    @classmethod
    def replace_all_terms(
        cls,
        session: Session,
        classification: Classification,
        *,
        substituents: list[str],
        predicted_chebi_terms: list[str],
        predicted_lipidmaps_terms: list[str],
    ) -> None:
        cls.replace_substituents(
            session=session,
            classification=classification,
            substituents=substituents,
        )

        cls.replace_predicted_chebi_terms(
            session=session,
            classification=classification,
            terms=predicted_chebi_terms,
        )

        cls.replace_predicted_lipidmaps_terms(
            session=session,
            classification=classification,
            terms=predicted_lipidmaps_terms,
        )

    @classmethod
    def replace_substituents(
        cls,
        session: Session,
        classification: Classification,
        substituents: list[str],
    ) -> None:
        links: list[ClassificationSubstituent] = []

        for name in substituents:
            substituent = get_or_create(
                session=session,
                model=Substituent,
                lookup={"substituent_name": name},
            )

            link = ClassificationSubstituent(
                classification_id=classification.classification_id,
                substituent_id=substituent.substituent_id,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="substituent_links",
            new_items=links,
        )

    @classmethod
    def replace_predicted_chebi_terms(
        cls,
        session: Session,
        classification: Classification,
        terms: list[str],
    ) -> None:
        links: list[ClassificationPredictedChebiTerm] = []

        for term in terms:
            stored_term = get_or_create(
                session=session,
                model=PredictedChebiTerm,
                lookup={"term_name": term},
            )

            link = ClassificationPredictedChebiTerm(
                classification_id=classification.classification_id,
                predicted_chebi_term_id=stored_term.predicted_chebi_term_id,
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="predicted_chebi_term_links",
            new_items=links,
        )

    @classmethod
    def replace_predicted_lipidmaps_terms(
        cls,
        session: Session,
        classification: Classification,
        terms: list[str],
    ) -> None:
        links: list[ClassificationPredictedLipidmapsTerm] = []

        for term in terms:
            stored_term = get_or_create(
                session=session,
                model=PredictedLipidmapsTerm,
                lookup={"term_name": term},
            )

            link = ClassificationPredictedLipidmapsTerm(
                classification_id=classification.classification_id,
                predicted_lipidmaps_term_id=(
                    stored_term.predicted_lipidmaps_term_id
                ),
            )

            links.append(link)

        replace_relationship_items(
            session=session,
            parent=classification,
            relationship_name="predicted_lipidmaps_term_links",
            new_items=links,
        )