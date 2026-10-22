"""Keep semantic base types separate from source parameters and executable SQL."""

import copy
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import SEMANTIC_TYPES, SOURCE_TYPE, build, encode, read_json, validate

PACK_ROOT = ROOT / "validation/workspace-views"
spec = importlib.util.spec_from_file_location("type_test_view_pack", PACK_ROOT / "load_pack.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class TemplateTypesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mdl = build()
        cls.reference = read_json(ROOT / "validation/reference-contract.json")

    def test_every_public_field_has_a_base_type_and_separate_source_record(self):
        for model in self.mdl["models"]:
            record = self.reference[model["tableReference"]["table"]]
            self.assertEqual(set(record["source_types"]), {c["name"] for c in model["columns"]})
            for column in model["columns"]:
                with self.subTest(model=model["name"], field=column["name"]):
                    self.assertIn(column["type"], SEMANTIC_TYPES)
                    source = SOURCE_TYPE.fullmatch(record["source_types"][column["name"]])
                    self.assertIsNotNone(source)
                    self.assertEqual(source[1], column["type"])
                    self.assertNotIn("source_types", column.get("properties", {}))
        self.assertNotIn('"source_types"', encode(self.mdl))

    def test_known_source_parameters_and_unspecified_parameters_are_preserved(self):
        for table, field, original in (
            ("OPCH", "PaidSum", "DECIMAL(19,6)"),
            ("OPCH", "PaidSumFc", "DECIMAL(19,6)"),
            ("OPCH", "PaidSumSc", "DECIMAL(19,6)"),
            ("OJDT", "Ref1", "VARCHAR(200)"),
            ("OPCH", "CardCode", "VARCHAR(15)"),
        ):
            self.assertEqual(self.reference[table]["source_types"][field], original)
        # Some prior annotations were already bare types; do not invent physical parameters.
        bare = {
            value
            for table in self.reference.values()
            for value in table["source_types"].values()
            if "(" not in value
        }
        self.assertTrue({"VARCHAR", "DECIMAL", "CHAR"} <= bare)

    def test_noncanonical_or_incompatible_types_fail_with_the_field_name(self):
        for value in ("DECIMAL(19,6)", "decimal", "NUMERIC", "VARCHAR", "CustomType", "", None, []):
            with self.subTest(value=value):
                mdl = copy.deepcopy(self.mdl)
                model = next(m for m in mdl["models"] if m["name"] == "opch")
                column = next(c for c in model["columns"] if c["name"] == "PaidSum")
                column["type"] = value
                with self.assertRaisesRegex(ValueError, r"type.*opch\.PaidSum"):
                    validate(mdl, self.reference)

    def test_missing_invalid_or_incompatible_source_records_fail(self):
        for value in (None, "", "DECIMAL(invalid)", "decimal(19,6)", "VARCHAR(96)"):
            with self.subTest(value=value):
                reference = copy.deepcopy(self.reference)
                if value is None:
                    reference["OPCH"]["source_types"].pop("PaidSum")
                else:
                    reference["OPCH"]["source_types"]["PaidSum"] = value
                with self.assertRaisesRegex(ValueError, r"type.*opch\.PaidSum"):
                    validate(self.mdl, reference)
        for value in (None, [], "invalid"):
            with self.subTest(source_types=value):
                reference = copy.deepcopy(self.reference)
                reference["OPCH"]["source_types"] = value
                with self.assertRaisesRegex(ValueError, r"source type record in opch\."):
                    validate(self.mdl, reference)

    def test_extension_model_types_follow_the_same_rule_in_both_languages(self):
        records = read_json(PACK_ROOT / "source-field-types.json")["tables"]
        for language in ("zh-CN", "en"):
            for model in loader.load_pack(language)["models"]:
                record = records[model["tableReference"]["table"]]
                self.assertEqual(record["source"], model["properties"]["sap_b1_source"])
                self.assertEqual(set(record["source_types"]), {c["name"] for c in model["columns"]})
                for column in model["columns"]:
                    self.assertIn(column["type"], SEMANTIC_TYPES)
                    source = SOURCE_TYPE.fullmatch(record["source_types"][column["name"]])
                    self.assertIsNotNone(source)
                    self.assertEqual(source[1], column["type"])
        self.assertEqual(records["OBTL"]["source_types"]["Quantity"], "DECIMAL(19,6)")
        self.assertEqual(records["OIBQ"]["source_types"]["ItemCode"], "VARCHAR(50)")

    def test_sql_casts_and_type_literals_are_loaded_verbatim(self):
        statement = (
            "SELECT CAST(1.123456 AS DECIMAL(19,6)) AS amount, "
            "CAST('x' AS VARCHAR(96)) AS code, 'DECIMAL(19,6)' AS literal\n"
        )
        read_resource = loader._read_resource

        def resource(relative, suffix):
            return statement if suffix == ".sql" else read_resource(relative, suffix)

        with patch.object(loader, "_read_resource", side_effect=resource):
            for language in ("zh-CN", "en"):
                for view in loader.load_pack(language)["views"]:
                    self.assertEqual(view["statement"], statement)


if __name__ == "__main__":
    unittest.main()
