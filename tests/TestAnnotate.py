from __future__ import annotations

from datetime import datetime
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from local_classyfire.cli.annotators.mgf import annotate_mgf_file
from local_classyfire.cli.annotators.msp import annotate_msp_file
from local_classyfire.cli.main import build_parser
from local_classyfire.models import (
    ClassyFireClass,
    ClassyFireDirectParent,
    ClassyFireKingdom,
    ClassyFireMissingQuery,
    ClassyFireQuery,
    ClassyFireSubclass,
    ClassyFireSuperclass,
)
from local_classyfire.services.classyfire_client import ClassyFireNotFoundError
from local_classyfire.services.session import (
    create_session_factory,
    create_sqlite_engine,
    create_tables,
)
from sqlalchemy import select


TEST_INCHIKEY = "LFQSCWFLJHTTHZ-UHFFFAOYSA-N"
TEST_MISSING_INCHIKEY = "BSYNRYMUTXBXSQ-UHFFFAOYSA-N"


class TestAnnotate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_dir = Path(__file__).resolve().parent / "fixtures"

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.work_dir = Path(self.temp_dir.name)
        self.db_path = self.work_dir / "classyfire_cache.sqlite"
        self._create_classyfire_cache(self.db_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_annotate_msp_file_adds_classification_lines_from_cache(self) -> None:
        output_path = self.work_dir / "annotated.msp"

        with patch(
            "local_classyfire.services.classyfire_query_repository.fetch_classyfire_result",
            side_effect=AssertionError("ClassyFire API should not be called"),
        ):
            annotate_msp_file(
                input_path=self.fixture_dir / "annotate_input.msp",
                output_path=output_path,
                db_path=self.db_path,
                identifier="inchikey",
                batch_size=1,
                show_progress=False,
            )

        output_text = output_path.read_text()

        self.assertIn(f"INCHIKEY: {TEST_INCHIKEY}", output_text)
        self.assertIn("Kingdom: Organic compounds", output_text)
        self.assertIn("Superclass: Alcohols and polyols", output_text)
        self.assertIn("Class: Alcohols", output_text)
        self.assertIn("Subclass: Primary alcohols", output_text)
        self.assertIn("DirectParent: Ethanol", output_text)
        self.assertLess(
            output_text.index(f"INCHIKEY: {TEST_INCHIKEY}"),
            output_text.index("Kingdom: Organic compounds"),
        )
        self.assertLess(
            output_text.index("DirectParent: Ethanol"),
            output_text.index("Num Peaks: 2"),
        )

    def test_annotate_mgf_file_adds_classification_lines_from_cache(self) -> None:
        output_path = self.work_dir / "annotated.mgf"

        with patch(
            "local_classyfire.services.classyfire_query_repository.fetch_classyfire_result",
            side_effect=AssertionError("ClassyFire API should not be called"),
        ):
            annotate_mgf_file(
                input_path=self.fixture_dir / "annotate_input.mgf",
                output_path=output_path,
                db_path=self.db_path,
                identifier="inchikey",
                batch_size=1,
                show_progress=False,
            )

        output_text = output_path.read_text()

        self.assertIn(f"INCHIKEY={TEST_INCHIKEY}", output_text)
        self.assertIn("Kingdom=Organic compounds", output_text)
        self.assertIn("Superclass=Alcohols and polyols", output_text)
        self.assertIn("Class=Alcohols", output_text)
        self.assertIn("Subclass=Primary alcohols", output_text)
        self.assertIn("DirectParent=Ethanol", output_text)
        self.assertLess(
            output_text.index(f"INCHIKEY={TEST_INCHIKEY}"),
            output_text.index("Kingdom=Organic compounds"),
        )
        self.assertLess(
            output_text.index("DirectParent=Ethanol"),
            output_text.index("31.0184 100"),
        )


    def test_annotate_msdataset_accepts_add_tag(self) -> None:
        parser = build_parser()

        args = parser.parse_args(
            [
                "annotate",
                "msdataset",
                "--input",
                "input.msds",
                "--output",
                "output.msds",
                "--db",
                "classyfire_cache.sqlite",
                "--identifier-column",
                "SMILES",
                "--identifier-type",
                "smiles",
                "--add-tag",
            ]
        )

        self.assertTrue(args.add_tag)


    def test_annotate_retry_missing_updates_missing_updated_at(self) -> None:
        output_path = self.work_dir / "annotated_missing.msp"
        old_timestamp = datetime(2001, 1, 1, 0, 0, 0)
        self._create_missing_query(
            inchikey=TEST_MISSING_INCHIKEY,
            updated_at=old_timestamp,
        )

        with patch(
            "local_classyfire.services.classyfire_query_repository.fetch_classyfire_result",
            side_effect=ClassyFireNotFoundError("still missing"),
        ):
            annotate_msp_file(
                input_path=self.fixture_dir / "annotate_missing_input.msp",
                output_path=output_path,
                db_path=self.db_path,
                identifier="inchikey",
                batch_size=1,
                request_interval_seconds=0,
                retry_missing=True,
                show_progress=False,
            )

        missing_query = self._get_missing_query(TEST_MISSING_INCHIKEY)

        self.assertIsNotNone(missing_query)
        self.assertEqual(missing_query.reason, "not_found")
        self.assertIn("still missing", missing_query.message)
        self.assertGreater(missing_query.updated_at, old_timestamp)

    def _create_classyfire_cache(self, db_path: Path) -> None:
        engine = create_sqlite_engine(db_path)
        create_tables(engine)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            kingdom = ClassyFireKingdom(name="Organic compounds")
            superclass = ClassyFireSuperclass(name="Alcohols and polyols")
            classyfire_class = ClassyFireClass(name="Alcohols")
            subclass = ClassyFireSubclass(name="Primary alcohols")
            direct_parent = ClassyFireDirectParent(name="Ethanol")

            session.add_all(
                [
                    kingdom,
                    superclass,
                    classyfire_class,
                    subclass,
                    direct_parent,
                ]
            )
            session.flush()

            session.add(
                ClassyFireQuery(
                    inchikey=TEST_INCHIKEY,
                    smiles="CCO",
                    kingdom_id=kingdom.classyfire_kingdom_id,
                    superclass_id=superclass.classyfire_superclass_id,
                    class_id=classyfire_class.classyfire_class_id,
                    subclass_id=subclass.classyfire_subclass_id,
                    direct_parent_id=direct_parent.classyfire_direct_parent_id,
                )
            )
            session.commit()

    def _create_missing_query(
        self,
        *,
        inchikey: str,
        updated_at: datetime,
    ) -> None:
        engine = create_sqlite_engine(self.db_path)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            session.add(
                ClassyFireMissingQuery(
                    inchikey=inchikey,
                    reason="old_reason",
                    message="old_message",
                    created_at=updated_at,
                    updated_at=updated_at,
                )
            )
            session.commit()

    def _get_missing_query(self, inchikey: str) -> ClassyFireMissingQuery | None:
        engine = create_sqlite_engine(self.db_path)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            return session.execute(
                select(ClassyFireMissingQuery)
                .where(ClassyFireMissingQuery.inchikey == inchikey)
            ).scalar_one_or_none()


if __name__ == "__main__":
    unittest.main()
