"""Ledger identity and amount examples using the template's actual relationship conditions."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build, read_json


class FinanceTest(unittest.TestCase):
    def setUp(self) -> None:
        mdl = build()
        self.models = {m["name"]: m for m in mdl["models"]}
        self.relationships = {r["name"]: r for r in mdl["relationships"]}
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.create(
            "ojdt",
            [
                "TransId",
                "Series",
                "Number",
                "Project",
                "LocTotal",
                "Ref1",
                "Ref2",
                "Ref3",
            ],
        )
        self.create(
            "jdt1",
            [
                "TransId",
                "Line_ID",
                "Account",
                "ShortName",
                "Project",
                "Debit",
                "Credit",
                "FCCurrency",
                "FCDebit",
                "FCCredit",
                "Ref1",
                "Ref2",
                "Ref3Line",
            ],
        )
        self.create("oact", ["AcctCode", "AcctName", "FormatCode", "ActCurr"])
        self.create("oprj", ["PrjCode", "PrjName", "Active"])
        self.db.executescript("""
            INSERT INTO ojdt (TransId,Series,Number,Project,LocTotal) VALUES
                (10,1,900,'HEAD-A',100),(20,2,900,'HEAD-B',20);
            INSERT INTO jdt1 (TransId,Line_ID,Account,ShortName,Project,Debit,Credit,
                FCCurrency,FCDebit,FCCredit) VALUES
                (10,0,'INTERNAL-A','BP-1','LINE-A',100,0,'USD',10,0),
                (10,1,'INTERNAL-B','INTERNAL-B',NULL,0,100,NULL,0,0),
                (20,0,'INTERNAL-A','BP-2','LINE-B',20,0,'EUR',10,0);
            INSERT INTO oact (AcctCode,AcctName,FormatCode,ActCurr) VALUES
                ('INTERNAL-A','Account A','100-01','##'),('INTERNAL-B','Account B','200-01','USD');
            INSERT INTO oprj (PrjCode,PrjName,Active) VALUES
                ('HEAD-A','Header A','Y'),('HEAD-B','Header B','Y'),
                ('LINE-A','Same name','N'),('LINE-B','Same name','Y');
        """)

    def create(self, name: str, selected: list[str]) -> None:
        model = self.models[name]
        columns = {c["name"]: c for c in model["columns"]}
        definitions = []
        for field in selected:
            column = columns[field]
            kind = (
                "NUMERIC"
                if column["type"].startswith(("DECIMAL", "INTEGER", "SMALLINT"))
                else "TEXT"
            )
            definitions.append(
                f'"{field}" {kind}' + (" NOT NULL" if column.get("notNull") else "")
            )
        primary = model["primaryKey"]
        primary = [primary] if isinstance(primary, str) else primary
        definitions.append("PRIMARY KEY (" + ",".join(primary) + ")")
        for key in model.get("uniqueKeys", []):
            if set(key) <= set(selected):
                definitions.append("UNIQUE (" + ",".join(key) + ")")
        self.db.execute(f"CREATE TABLE {name} (" + ",".join(definitions) + ")")

    def condition(self, name: str) -> str:
        return self.relationships[name]["condition"]

    def test_composite_line_identity_keeps_zero_rows_and_rejects_missing_key(
        self,
    ) -> None:
        self.assertEqual(
            self.db.execute("SELECT TransId,Line_ID FROM jdt1 ORDER BY 1,2").fetchall(),
            [(10, 0), (10, 1), (20, 0)],
        )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO jdt1 (TransId,Line_ID) VALUES (10,NULL)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO jdt1 (TransId,Line_ID) VALUES (NULL,2)")
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO jdt1 (TransId,Line_ID) VALUES (10,0)")

    def test_display_number_collision_does_not_mix_journal_headers(self) -> None:
        rows = self.db.execute(
            "SELECT jdt1.TransId,jdt1.Line_ID,ojdt.Series,ojdt.Number "
            f"FROM jdt1 JOIN ojdt ON {self.condition('ojdt_jdt1')} ORDER BY 1,2"
        ).fetchall()
        self.assertEqual(rows, [(10, 0, 1, 900), (10, 1, 1, 900), (20, 0, 2, 900)])

    def test_bp_short_name_and_formatted_code_do_not_replace_account_key(self) -> None:
        rows = self.db.execute(
            "SELECT jdt1.TransId,jdt1.Line_ID,oact.AcctName,oact.FormatCode "
            f"FROM jdt1 JOIN oact ON {self.condition('jdt1_oact')} ORDER BY 1,2"
        ).fetchall()
        self.assertEqual(
            rows,
            [
                (10, 0, "Account A", "100-01"),
                (10, 1, "Account B", "200-01"),
                (20, 0, "Account A", "100-01"),
            ],
        )

    def test_line_and_header_projects_stay_independent(self) -> None:
        line = self.db.execute(
            "SELECT jdt1.TransId,jdt1.Line_ID,oprj.PrjCode,oprj.PrjName "
            f"FROM jdt1 JOIN oprj ON {self.condition('sap_jdt1_oprj')} ORDER BY 1,2"
        ).fetchall()
        head = self.db.execute(
            "SELECT ojdt.TransId,oprj.PrjCode FROM ojdt JOIN oprj ON "
            f"{self.condition('sap_ojdt_oprj')} ORDER BY 1"
        ).fetchall()
        self.assertEqual(
            line, [(10, 0, "LINE-A", "Same name"), (20, 0, "LINE-B", "Same name")]
        )
        self.assertEqual(head, [(10, "HEAD-A"), (20, "HEAD-B")])

    def test_retaining_join_preserves_empty_unknown_and_inactive_projects(self) -> None:
        self.db.execute(
            "INSERT INTO jdt1 (TransId,Line_ID,Project) VALUES (20,1,'UNKNOWN')"
        )
        rows = self.db.execute(
            "SELECT jdt1.TransId,jdt1.Line_ID,oprj.PrjCode,oprj.Active "
            f"FROM jdt1 LEFT JOIN oprj ON {self.condition('sap_jdt1_oprj')} ORDER BY 1,2"
        ).fetchall()
        self.assertEqual(
            rows,
            [
                (10, 0, "LINE-A", "N"),
                (10, 1, None, None),
                (20, 0, "LINE-B", "Y"),
                (20, 1, None, None),
            ],
        )

    def test_header_total_requires_header_grain(self) -> None:
        correct = self.db.execute("SELECT SUM(LocTotal) FROM ojdt").fetchone()[0]
        duplicated = self.db.execute(
            "SELECT SUM(ojdt.LocTotal) FROM ojdt JOIN jdt1 ON "
            + self.condition("ojdt_jdt1")
        ).fetchone()[0]
        self.assertEqual(correct, 120)
        self.assertEqual(duplicated, 220)

    def test_both_reversal_styles_keep_stored_signs(self) -> None:
        self.db.execute("DELETE FROM jdt1")
        self.db.executemany(
            "INSERT INTO jdt1 (TransId,Line_ID,Debit,Credit) VALUES (?,?,?,?)",
            [(10, 0, 100, 0), (10, 1, -100, 0), (20, 0, 100, 0), (20, 1, 0, 100)],
        )
        rows = self.db.execute(
            "SELECT TransId,SUM(Debit-Credit) FROM jdt1 GROUP BY TransId ORDER BY 1"
        ).fetchall()
        self.assertEqual(rows, [(10, 0), (20, 0)])
        for field in ("Debit", "Credit"):
            column = next(
                c for c in self.models["jdt1"]["columns"] if c["name"] == field
            )
            self.assertFalse(column["isCalculated"])

    def test_foreign_currency_groups_do_not_use_account_currency_sentinel(self) -> None:
        self.db.execute(
            "INSERT INTO jdt1 (TransId,Line_ID,Account,FCCurrency,FCDebit,FCCredit) "
            "VALUES (20,1,'INTERNAL-A',NULL,5,0)"
        )
        rows = self.db.execute(
            "SELECT jdt1.FCCurrency,SUM(jdt1.FCDebit-jdt1.FCCredit) "
            f"FROM jdt1 JOIN oact ON {self.condition('jdt1_oact')} GROUP BY jdt1.FCCurrency "
            "ORDER BY jdt1.FCCurrency"
        ).fetchall()
        self.assertEqual(rows, [(None, 5), ("EUR", 10), ("USD", 10)])
        self.assertNotIn("##", [r[0] for r in rows])

    def test_reference_text_is_optional_200_char_metadata_and_not_identity(
        self,
    ) -> None:
        value = "R" * 200
        reference = read_json(ROOT / "validation/reference-contract.json")
        for model, fields in [
            ("ojdt", ["Ref1", "Ref2", "Ref3"]),
            ("jdt1", ["Ref1", "Ref2", "Ref3Line"]),
        ]:
            for field in fields:
                column = next(
                    c for c in self.models[model]["columns"] if c["name"] == field
                )
                self.assertEqual(column["type"], "VARCHAR")
                self.assertEqual(reference[model.upper()]["source_types"][field], "VARCHAR(200)")
                self.assertFalse(column["notNull"])
                self.assertNotIn(field, self.models[model]["primaryKey"])
                self.db.execute(f"UPDATE {model} SET {field}=?", (value,))
                self.assertEqual(
                    self.db.execute(f"SELECT DISTINCT {field} FROM {model}").fetchall(),
                    [(value,)],
                )


if __name__ == "__main__":
    unittest.main()
