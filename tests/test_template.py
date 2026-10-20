"""Portable template invariants and representative join behavior, without Frappe or network."""

from __future__ import annotations

import copy
import json
import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build, encode, read_json, validate  # noqa: E402


class TemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mdl = build()
        cls.reference = read_json(ROOT / "validation" / "reference-contract.json")

    def test_committed_artifact_is_reproducible(self) -> None:
        self.assertEqual((ROOT / "mdl.json").read_text(encoding="utf-8"), encode(self.mdl))

    def test_artifact_has_no_customer_connection_or_instance_policy(self) -> None:
        text = json.dumps(self.mdl, ensure_ascii=False)
        self.assertNotRegex(
            text, r"(?i)customer_fixture_alpha|customer_fixture_beta|192\.168\.|internal_fixture\.example|/home/|password|row_security"
        )
        self.assertNotIn("本项目", text)
        self.assertNotIn("当前客户", text)
        self.assertEqual(self.mdl["catalog"], "sap_b1")
        self.assertFalse(self.mdl["views"])
        self.assertFalse(self.mdl["cubes"])

    def test_customer_column_cannot_enter_template(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["models"][0]["columns"][0]["name"] = "U_PrivateCode"
        with self.assertRaisesRegex(ValueError, "Customer or calculated"):
            validate(mdl, self.reference)

    def test_customer_calculation_cannot_enter_template(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["models"][0]["columns"][0]["isCalculated"] = True
        with self.assertRaisesRegex(ValueError, "Customer or calculated"):
            validate(mdl, self.reference)

    def test_customer_catalog_cannot_enter_template(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["models"][0]["tableReference"]["catalog"] = "private_company"
        with self.assertRaisesRegex(ValueError, "Physical company catalog"):
            validate(mdl, self.reference)

    def test_instance_policy_cannot_enter_template(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["models"][0]["rowLevelSecurity"] = {"tenant": "example"}
        with self.assertRaisesRegex(ValueError, "Instance or unsupported model"):
            validate(mdl, self.reference)

    def test_missing_relationship_column_fails(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["relationships"][0]["condition"] = "crd1.U_PrivateCode = ocrd.CardCode"
        with self.assertRaisesRegex(ValueError, "Missing relationship column"):
            validate(mdl, self.reference)

    def test_relationship_cannot_reference_third_model(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        mdl["relationships"][0]["condition"] += " AND oitm.ItemCode = 'example'"
        with self.assertRaisesRegex(ValueError, "exactly its two models"):
            validate(mdl, self.reference)

    def test_compound_primary_key_cannot_be_shortened(self) -> None:
        mdl = copy.deepcopy(self.mdl)
        model = next(item for item in mdl["models"] if item["name"] == "dln1")
        model["primaryKey"] = "DocEntry"
        with self.assertRaisesRegex(ValueError, "Primary key differs"):
            validate(mdl, self.reference)

    def test_reviewed_instance_edges_are_not_promoted_to_generic_defaults(self) -> None:
        relationships = {item["name"] for item in self.mdl["relationships"]}
        excluded = read_json(ROOT / "validation" / "deferred.json")["excluded_legacy_relationships"]
        self.assertTrue(excluded)
        self.assertFalse(relationships & {item["name"] for item in excluded})
        for relation in self.mdl["relationships"]:
            self.assertNotIn(set(relation["models"]), [{"oivl", "ige1"}, {"oivl", "ign1"}, {"oivl", "wtr1"}])
            self.assertNotIn(set(relation["models"]), [{"ige1", "wor1"}])

    def test_payment_business_partner_branches_keep_both_discriminators(self) -> None:
        relationships = self.mdl["relationships"]
        for payment in ("orct", "ovpm"):
            matches = [item for item in relationships if set(item["models"]) == {payment, "ocrd"}]
            self.assertEqual(len(matches), 2)
            for relation in matches:
                self.assertIn(f"{payment}.DocType = ", relation["condition"])
                self.assertIn("ocrd.CardType = ", relation["condition"])

    def test_source_type_excludes_same_number_from_other_document_type(self) -> None:
        relation = next(item for item in self.mdl["relationships"] if item["name"] == "sap_inv1_rdr1")
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(
                "CREATE TABLE inv1 (DocEntry INT, BaseEntry INT, BaseLine INT, BaseType INT);"
                "CREATE TABLE rdr1 (DocEntry INT, LineNum INT);"
                "INSERT INTO rdr1 VALUES (100, 0);"
                "INSERT INTO inv1 VALUES (1, 100, 0, 17), (2, 100, 0, 15);"
            )
            rows = connection.execute("SELECT inv1.DocEntry FROM inv1 JOIN rdr1 ON " + relation["condition"])
            self.assertEqual(rows.fetchall(), [(1,)])

    def test_document_line_join_does_not_fan_out_to_other_source_lines(self) -> None:
        relation = next(item for item in self.mdl["relationships"] if item["name"] == "rdr1_dln1")
        with sqlite3.connect(":memory:") as connection:
            connection.executescript(
                "CREATE TABLE dln1 (DocEntry INT, BaseEntry INT, BaseLine INT, BaseType INT);"
                "CREATE TABLE rdr1 (DocEntry INT, LineNum INT);"
                "INSERT INTO rdr1 VALUES (100, 0), (100, 1);"
                "INSERT INTO dln1 VALUES (200, 100, 1, 17);"
            )
            rows = connection.execute("SELECT rdr1.LineNum FROM rdr1 JOIN dln1 ON " + relation["condition"])
            self.assertEqual(rows.fetchall(), [(1,)])

    def test_price_list_is_not_an_inventory_cost_default(self) -> None:
        model = next(item for item in self.mdl["models"] if item["name"] == "itm1")
        description = model["properties"]["description"]
        self.assertNotRegex(description, r"价目表\s*1")
        self.assertIn("不默认", description)

    def test_official_field_case_and_reference_links_are_preserved(self) -> None:
        model = next(item for item in self.mdl["models"] if item["name"] == "oitm")
        names = {item["name"] for item in model["columns"]}
        self.assertIn("LeadTime", names)
        self.assertNotIn("LEADTIME", names)
        for item in self.mdl["models"]:
            self.assertRegex(item["properties"]["sap_b1_source"], r"^https://help\.sap\.com/")


if __name__ == "__main__":
    unittest.main()
