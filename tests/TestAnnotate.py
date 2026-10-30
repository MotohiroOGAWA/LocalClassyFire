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
import msentity as ms
import numpy as np

from local_classyfire.cli.annotators.msdataset import (
    CLASSIFICATION_COLUMNS,
    annotate_msdataset,
)
from local_classyfire.cli.commands.annotate import write_annotated_msdataset


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


    def test_lookup_smiles_uses_default_db(self) -> None:
        parser = build_parser()
        expected_db_path = str(
            Path(__file__).resolve().parents[1] / "db" / "classyfire_cache.sqlite"
        )

        args = parser.parse_args(
            [
                "lookup",
                "smiles",
                "CCO",
            ]
        )

        self.assertEqual(args.db, expected_db_path)


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

    def test_msdataset_classifies_duplicates_and_preserves_peaks(self) -> None:
        with ms.from_peaks([[(31.0, 100.0)], [], [(45.0, 200.0)]]) as dataset:
            dataset["SMILES"] = ["CCO", None, " CCO "]
            dataset["Name"] = ["first", "missing", "duplicate"]
            dataset.description = "test spectra"
            dataset.set_attribute("source", "test")
            dataset.set_peak_column("formula", ["CH3O", "C2H5O"])
            with patch(
                "local_classyfire.services.classyfire_query_repository.fetch_classyfire_result",
                side_effect=AssertionError("ClassyFire API should not be called"),
            ):
                annotate_msdataset(
                    dataset=dataset, db_path=self.db_path,
                    identifier_column="SMILES", identifier_type="smiles",
                    batch_size=1, show_progress=False,
                )
            self.assertEqual(dataset["Kingdom"], ["Organic compounds", None, "Organic compounds"])
            self.assertEqual(dataset["DirectParent"], ["Ethanol", None, "Ethanol"])
            self.assertEqual(dataset.columns, ["SMILES", *CLASSIFICATION_COLUMNS, "Name"])
            dataset.add_tag("ClassyFire")
            for suffix in ("msds", "msp", "mgf"):
                with self.subTest(format=suffix):
                    path = self.work_dir / f"annotated.{suffix}"
                    write_annotated_msdataset(dataset=dataset, output_path=str(path))
                    with ms.load(path) as restored:
                        self.assertEqual(len(restored), 3)
                        np.testing.assert_array_equal(restored.mz, dataset.mz)
                        np.testing.assert_array_equal(restored.intensity, dataset.intensity)
                        self.assertEqual(restored[0]["Kingdom"], "Organic compounds")
                        self.assertEqual(restored[2]["DirectParent"], "Ethanol")
                        if suffix == "msds":
                            self.assertEqual(restored.columns, dataset.columns)
                            self.assertEqual(restored.tags, ["ClassyFire"])
                            self.assertEqual(restored.description, dataset.description)
                            self.assertEqual(restored.attributes, dataset.attributes)
                            self.assertEqual(restored.peak_column("formula"), ["CH3O", "C2H5O"])

    def test_msdataset_no_overwrite_preserves_existing_columns(self) -> None:
        with ms.from_peaks([[], []]) as dataset:
            dataset["SMILES"] = ["CCO", None]
            dataset["Kingdom"] = ["existing", "missing record"]
            annotate_msdataset(
                dataset=dataset, db_path=self.db_path,
                identifier_column="SMILES", identifier_type="smiles",
                overwrite=False, show_progress=False,
            )
            self.assertEqual(dataset["Kingdom"], ["existing", "missing record"])
            self.assertEqual(dataset["DirectParent"], ["Ethanol", None])

    def test_msdataset_missing_identifiers_and_empty_dataset(self) -> None:
        for identifiers in ([None, "", "  "], []):
            with self.subTest(identifiers=identifiers):
                with ms.from_peaks([[] for _ in identifiers]) as dataset:
                    dataset["SMILES"] = identifiers
                    with patch(
                        "local_classyfire.cli.annotators.msdataset.lookup_classification_batch",
                        side_effect=AssertionError("Missing identifiers should not be queried"),
                    ):
                        annotate_msdataset(
                            dataset=dataset, db_path=self.db_path,
                            identifier_column="SMILES", identifier_type="smiles",
                            show_progress=False,
                        )
                    for column in CLASSIFICATION_COLUMNS:
                        self.assertIn(column, dataset.columns)
                        self.assertEqual(dataset[column], [None] * len(identifiers))

    def test_msdataset_cli_adds_tag_and_writes_hdf5_alias(self) -> None:
        input_path = self.work_dir / "input.msds"
        with ms.from_peaks([[(31.0, 100.0)]]) as dataset:
            dataset["SMILES"] = ["CCO"]
            dataset.save(input_path)
        output_path = self.work_dir / "nested" / "classified.h5"
        args = build_parser().parse_args([
            "annotate", "msdataset", "-i", str(input_path), "-o", str(output_path),
            "--db", str(self.db_path), "--identifier-column", "SMILES",
            "--identifier-type", "smiles", "--add-tag",
        ])
        args.func(args)
        with ms.load(output_path.with_suffix(".msds")) as restored:
            self.assertEqual(restored["DirectParent"], ["Ethanol"])
            self.assertEqual(restored.tags, ["ClassyFire"])

    def test_text_formats_accept_custom_identifier_columns(self) -> None:
        for file_type in ("msp", "mgf"):
            for identifier_type, column, value in (
                ("smiles", "SMILES", "CCO"),
                ("inchikey", "INCHIKEY", TEST_INCHIKEY),
            ):
                with self.subTest(format=file_type, identifier=identifier_type):
                    delimiter = ": " if file_type == "msp" else "="
                    original = (self.fixture_dir / f"annotate_input.{file_type}").read_text()
                    # Keep a conflicting default column to verify the explicit selection.
                    custom_column = column.lower() + "1"
                    text = original.replace(
                        f"{column}{delimiter}{value}",
                        f"{column}{delimiter}INVALID\n{custom_column}{delimiter}{value}",
                    )
                    self.assertNotEqual(text, original)
                    input_path = self.work_dir / f"custom.{file_type}"
                    output_path = self.work_dir / f"custom_classified.{file_type}"
                    input_path.write_text(text)
                    args = build_parser().parse_args([
                        "annotate", file_type, "-i", str(input_path), "-o", str(output_path),
                        "--db", str(self.db_path), "--identifier-type", identifier_type,
                        "--identifier-column", column + "1", "--no-progress",
                    ])
                    with patch(
                        "local_classyfire.services.classyfire_query_repository.fetch_classyfire_result",
                        side_effect=AssertionError("Only the selected cached identifier should be queried"),
                    ):
                        args.func(args)
                    output = output_path.read_text()
                    self.assertIn(f"{custom_column}{delimiter}{value}", output)
                    self.assertIn(f"DirectParent{delimiter}Ethanol", output)
                    self.assertIn(f"{column}{delimiter}INVALID", output)

    def test_identifier_arguments_are_shared_by_all_formats(self) -> None:
        from local_classyfire.cli.commands.annotate import resolve_identifier_column

        for file_type in ("msp", "mgf", "msdataset", "msds"):
            base = ["annotate", file_type, "-i", "input", "-o", "output", "--db", "cache.sqlite"]
            with self.subTest(format=file_type):
                args = build_parser().parse_args(base)
                self.assertEqual(args.identifier_type, "inchikey")
                self.assertEqual(resolve_identifier_column(args), "InChIKey")
                args = build_parser().parse_args(base + ["--identifier-type", "smiles"])
                self.assertEqual(resolve_identifier_column(args), "SMILES")
                args = build_parser().parse_args(base + ["--identifier", "smiles", "--identifier-column", "SMILES1"])
                self.assertEqual(args.identifier_type, "smiles")
                self.assertEqual(resolve_identifier_column(args), "SMILES1")

    def test_custom_text_column_does_not_fall_back_to_default(self) -> None:
        from local_classyfire.cli.annotators.text_records import find_identifier_in_line

        self.assertIsNone(find_identifier_in_line(
            "SMILES: CCO", identifier="smiles", identifier_column="SMILES1",
        ))
        self.assertEqual(find_identifier_in_line(
            "sMiLeS_1: c1ccccc1", identifier="smiles", identifier_column="SMILES1",
        ), ("smiles", "c1ccccc1"))

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
