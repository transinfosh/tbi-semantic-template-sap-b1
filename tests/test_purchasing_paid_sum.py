"""OPCH paid-sum coverage and investigation SQL; no SAP update behavior is simulated."""

import copy
import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build, read_json, validate

FAMILY = {"PaidSum": "PaidToDate", "PaidSumFc": "PaidFC", "PaidSumSc": "PaidSys"}


class PurchasingPaidSumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mdl = build()
        cls.opch = next(model for model in cls.mdl["models"] if model["name"] == "opch")
        cls.reference = read_json(ROOT / "validation/reference-contract.json")

    def test_both_paid_families_are_distinct_physical_header_fields(self):
        self.assertEqual(self.opch["tableReference"], {"schema": "dbo", "table": "OPCH"})
        self.assertEqual(self.opch["primaryKey"], "DocEntry")
        for name in (*FAMILY, *FAMILY.values()):
            with self.subTest(name=name):
                fields = [field for field in self.opch["columns"] if field["name"] == name]
                self.assertEqual(len(fields), 1)
                field = fields[0]
                self.assertEqual(field["type"], "DECIMAL")
                self.assertEqual(self.reference["OPCH"]["source_types"][name], "DECIMAL(19,6)")
                self.assertFalse(field["isCalculated"])
                self.assertFalse(field["isHidden"])
                self.assertFalse(field["notNull"])
                self.assertIn(name, self.reference["OPCH"]["columns"])
                self.assertEqual(
                    field["properties"]["sap_b1_source"], self.reference["OPCH"]["source"]
                )

    def test_wrong_case_duplicates_and_calculations_are_rejected(self):
        for name in FAMILY:
            for mutation, error in (
                ("case", "Unsupported or undocumented"),
                ("duplicate", "Invalid or duplicate"),
                ("calculation", "Customer or calculated"),
            ):
                with self.subTest(name=name, mutation=mutation):
                    mdl = copy.deepcopy(self.mdl)
                    model = next(model for model in mdl["models"] if model["name"] == "opch")
                    field = next(field for field in model["columns"] if field["name"] == name)
                    if mutation == "case":
                        field["name"] = name.upper()
                    elif mutation == "duplicate":
                        model["columns"].append(copy.deepcopy(field))
                    else:
                        field["isCalculated"] = True
                    with self.assertRaisesRegex(ValueError, error):
                        validate(mdl, self.reference)

    def test_bilingual_definitions_keep_evidence_limits_and_no_aliases(self):
        translated = read_json(ROOT / "locales/en.json")["models"]["opch"]["columns"]
        columns = {field["name"]: field for field in self.opch["columns"]}
        for name, counterpart in FAMILY.items():
            with self.subTest(name=name):
                chinese = columns[name]["properties"]["description"]
                english = translated[name]["description"]
                self.assertIn(counterpart, chinese)
                self.assertIn(counterpart, english)
                self.assertIn("更新边界未确认", chinese)
                self.assertIn("remain unconfirmed", english)
                self.assertIn("不能直接用于通用未清应付公式", chinese)
                self.assertIn("Do not use directly for a general open-payables formula", english)
                self.assertIn(name, columns[counterpart]["properties"]["description"])
                self.assertIn(name, translated[counterpart]["description"])
        self.assertIn("推定", columns["PaidSum"]["properties"]["description"])
        self.assertIn("pending verification", translated["PaidSum"]["description"])
        self.assertNotIn("LC", translated["PaidSum"]["displayName"])
        for name, currency in (("PaidSumFc", "DocCur"), ("PaidSumSc", "OADM.SysCurrncy")):
            self.assertIn(currency, columns[name]["properties"]["description"])
            self.assertIn(currency, translated[name]["description"])

    def test_restoration_is_recorded_without_rewriting_original_deletions(self):
        selection = read_json(ROOT / "validation/cross-module-field-selection.json")
        self.assertEqual(selection["version"], "0.8.0")
        self.assertIn("PaidSum", selection["models"]["opch"]["removed"])
        revision = next(change for change in selection["revisions"] if change["version"] == "0.8.2")
        actions = revision["models"]["opch"]
        self.assertEqual(actions["restored"], ["PaidSum"])
        self.assertEqual(set(actions["added"]), {"PaidSumFc", "PaidSumSc"})
        self.assertEqual(set(actions["metadata_changed"]), set(FAMILY.values()))

    def test_audit_retains_currency_differences_nulls_signs_and_all_statuses(self):
        sql = (ROOT / "validation/opch-paid-sum-audit.sql").read_text(encoding="utf-8")
        with closing(sqlite3.connect(":memory:")) as db:
            db.row_factory = sqlite3.Row
            db.execute("ATTACH DATABASE ':memory:' AS dbo")
            db.execute(
                "CREATE TABLE dbo.OPCH (DocEntry INTEGER PRIMARY KEY, CANCELED TEXT, "
                "DocManClsd TEXT, DocStatus TEXT, DocCur TEXT, "
                "DocTotal NUMERIC, DocTotalFC NUMERIC, DocTotalSy NUMERIC, "
                "PaidSum NUMERIC, PaidSumFc NUMERIC, PaidSumSc NUMERIC, "
                "PaidToDate NUMERIC, PaidFC NUMERIC, PaidSys NUMERIC)"
            )
            # Deliberate counterexamples, not customer rows or claims about SAP event effects.
            samples = [
                {},
                {"PaidSum": 41},
                {"DocManClsd": "Y", "DocStatus": "C", "PaidSumSc": 81},
                {"CANCELED": "Y", "DocStatus": "C", "PaidSumFc": 21},
                {"CANCELED": "C", "DocStatus": "C", "PaidSum": -40},
                {"PaidSum": -20, "PaidToDate": -30},
                {"PaidSum": None, "PaidSumFc": None, "PaidSumSc": None},
                {"PaidToDate": None, "PaidFC": None, "PaidSys": None},
                dict.fromkeys((*FAMILY, *FAMILY.values()), 0),
            ]
            for entry, overrides in enumerate(samples, 1):
                row = {
                    "DocEntry": entry, "CANCELED": "N", "DocManClsd": "N", "DocStatus": "O",
                    "DocCur": "EUR", "DocTotal": 200, "DocTotalFC": 100, "DocTotalSy": 400,
                    "PaidSum": 40, "PaidSumFc": 20, "PaidSumSc": 80,
                    "PaidToDate": 40, "PaidFC": 20, "PaidSys": 80,
                } | overrides
                db.execute(
                    f"INSERT INTO dbo.OPCH ({','.join(row)}) VALUES ({','.join('?' for _ in row)})",
                    tuple(row.values()),
                )
            # SQLite authorizes only a read; a mutation added to the audit must fail.
            db.set_authorizer(
                lambda action, *_: sqlite3.SQLITE_OK
                if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ)
                else sqlite3.SQLITE_DENY
            )
            rows = {row["DocEntry"]: row for row in db.execute(sql)}
            self.assertEqual(list(rows), list(range(1, 10)))
            self.assertEqual(rows[2]["PaidSumComparison"], "DIFFERENT")
            self.assertEqual(rows[2]["PaidSumFcComparison"], "MATCH")
            self.assertEqual(rows[2]["PaidSumDifference"], 1)
            self.assertEqual(rows[3]["DocManClsd"], "Y")
            self.assertEqual(rows[3]["PaidSumScComparison"], "DIFFERENT")
            self.assertEqual(rows[4]["CANCELED"], "Y")
            self.assertEqual(rows[4]["PaidSumFcComparison"], "DIFFERENT")
            self.assertEqual(rows[5]["CANCELED"], "C")
            self.assertEqual(rows[5]["PaidSum"], -40)
            self.assertEqual(rows[6]["PaidSumDifference"], 10)
            for name in FAMILY:
                self.assertEqual(rows[1][name + "Comparison"], "MATCH")
                for entry in (7, 8):
                    self.assertEqual(rows[entry][name + "Comparison"], "UNKNOWN_NULL")
                    self.assertIsNone(rows[entry][name + "Difference"])
                self.assertEqual(rows[9][name], 0)
                self.assertEqual(rows[9][name + "Comparison"], "MATCH")


if __name__ == "__main__":
    unittest.main()
