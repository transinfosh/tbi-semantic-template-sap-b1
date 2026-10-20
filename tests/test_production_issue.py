"""Synthetic production issue contracts; no customer rows, Frappe, or network."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build, read_json


class ProductionIssueTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mdl = build()

    def relationship(self, source: str, target: str) -> dict:
        matches = [item for item in self.mdl["relationships"] if item["models"] == [source, target]]
        self.assertEqual(len(matches), 1, f"Expected one {source} to {target} source relationship")
        self.assertEqual(matches[0]["joinType"], "MANY_TO_ONE")
        return matches[0]

    def issue_query(self, extra_sql: str = "") -> list[dict]:
        sql = (ROOT / "validation" / "production-issue-query.sql").read_text(encoding="utf-8")
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.row_factory = sqlite3.Row
            connection.executescript(
                "ATTACH DATABASE ':memory:' AS dbo;"
                "CREATE TABLE dbo.OWOR (DocEntry INT PRIMARY KEY, DocNum INT, Type TEXT);"
                "CREATE TABLE dbo.WOR1 (DocEntry INT, LineNum INT, ItemCode TEXT, IssueType TEXT, "
                "PRIMARY KEY (DocEntry, LineNum));"
                "CREATE TABLE dbo.OIGE (DocEntry INT PRIMARY KEY, DocDate TEXT, CreateDate TEXT, CANCELED TEXT);"
                "CREATE TABLE dbo.IGE1 (DocEntry INT, LineNum INT, BaseType INT, BaseEntry INT, BaseLine INT, "
                "ItemCode TEXT, ItemType INT, WhsCode TEXT, Quantity NUMERIC, InvQty NUMERIC, "
                "unitMsr TEXT, UomCode TEXT, UseBaseUn TEXT, NumPerMsr NUMERIC, "
                "StockSum NUMERIC, StockValue NUMERIC, LineTotal NUMERIC, StockPrice NUMERIC, "
                "PRIMARY KEY (DocEntry, LineNum));"
                "CREATE TABLE dbo.OITM (ItemCode TEXT PRIMARY KEY, InvntItem TEXT);"
                "CREATE TABLE dbo.OIVL (TransSeq INT PRIMARY KEY, TransType INT, CreatedBy INT, "
                "DocLineNum INT, InQty NUMERIC, OutQty NUMERIC, SumStock NUMERIC);"
                "CREATE TABLE dbo.IVL1 (TransSeq INT, LayerID INT, TransValue NUMERIC, "
                "CalcPrice NUMERIC, PRIMARY KEY (TransSeq, LayerID));"
                "INSERT INTO dbo.OWOR VALUES (101, 7001, 'S'), (102, 7002, 'S');"
                "INSERT INTO dbo.WOR1 VALUES (101, 7, 'MATERIAL-A', 'M'), (101, 8, 'SERVICE-A', 'B'), "
                "(102, 7, 'MATERIAL-A', 'M');"
                "INSERT INTO dbo.OIGE VALUES (500, '2024-05-10', '2024-05-12', 'N'), "
                "(501, '2024-05-20', '2024-05-20', 'N'), (502, '2023-01-01', '2023-01-01', 'N'), "
                "(503, '2024-05-22', '2024-05-22', 'N');"
                "INSERT INTO dbo.OITM VALUES ('MATERIAL-A', 'Y'), ('SERVICE-A', 'N');"
                "INSERT INTO dbo.IGE1 VALUES "
                "(500, 0, 202, 101, 7, 'MATERIAL-A', 4, 'W1', 2, 20, 'box', 'BOX', 'N', 10, 224, 0, 999, 11.2), "
                "(500, 1, 202, 101, 8, 'SERVICE-A', 4, 'W1', 3, 3, 'hour', 'H', 'Y', 1, 0, 0, 60, 0), "
                "(501, 0, 202, 101, 7, 'MATERIAL-A', 4, 'W1', 1, 10, 'box', 'BOX', 'N', 10, 0, 0, 777, 0), "
                "(502, 0, 202, 102, 7, 'MATERIAL-A', 4, 'W1', 1, 100, 'box', 'BOX', 'N', 100, 999, 0, 999, 9.99), "
                "(503, 0, 202, 101, 7, 'MATERIAL-A', 4, 'W1', -2, -2, 'unit', 'EA', 'Y', 1, -24, 0, -24, 12);"
                "INSERT INTO dbo.OIVL VALUES (1001, 60, 500, 0, 0, 8, -80), "
                "(1002, 60, 500, 0, 0, 12, -144), (1003, 60, 501, 0, 0, 10, NULL), "
                "(1004, 59, 500, 0, 90, 0, 900), (1005, 60, 502, 0, 0, 100, -999), "
                "(1006, 60, 503, 0, 2, 0, 24);"
                "INSERT INTO dbo.IVL1 VALUES (1001, 1, -30, 10), (1001, 2, -50, 10), "
                "(1002, 1, -144, 12), (1003, 1, NULL, NULL), (1004, 1, 900, 10), "
                "(1005, 1, -999, 9.99), (1006, 1, 24, 12);"
            )
            if extra_sql:
                connection.executescript(extra_sql)
            return [dict(row) for row in connection.execute(sql, {"production_order_entry": 101})]

    def test_component_source_uses_base_line_and_work_order_not_item_code(self) -> None:
        relation = self.relationship("ige1", "wor1")
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                "CREATE TABLE ige1 (DocEntry INT, LineNum INT, BaseType INT, "
                "BaseEntry INT, BaseLine INT, ItemCode TEXT);"
                "CREATE TABLE wor1 (DocEntry INT, LineNum INT, ItemCode TEXT);"
                "INSERT INTO wor1 VALUES (101, 0, 'MATERIAL-A'), (101, 7, 'MATERIAL-A'), "
                "(102, 7, 'MATERIAL-A');"
                "INSERT INTO ige1 VALUES (500, 0, 202, 101, 7, 'MATERIAL-A'), "
                "(501, 0, 202, 102, 7, 'MATERIAL-A'), (502, 0, 17, 101, 7, 'MATERIAL-A');"
            )
            rows = connection.execute(
                "SELECT ige1.DocEntry, wor1.DocEntry, wor1.LineNum FROM ige1 JOIN wor1 ON "
                + relation["condition"]
                + " WHERE wor1.DocEntry = 101"
            )
            self.assertEqual(rows.fetchall(), [(500, 101, 7)])

    def test_valuation_source_keeps_transaction_type_and_all_transactions_per_line(self) -> None:
        relation = self.relationship("oivl", "ige1")
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                "CREATE TABLE ige1 (DocEntry INT, LineNum INT);"
                "CREATE TABLE oivl (TransSeq INT, TransType INT, CreatedBy INT, DocLineNum INT);"
                "INSERT INTO ige1 VALUES (500, 0), (500, 1);"
                "INSERT INTO oivl VALUES (1001, 60, 500, 0), (1002, 60, 500, 0), "
                "(1003, 59, 500, 0), (1004, 60, 500, 1);"
            )
            rows = connection.execute(
                "SELECT oivl.TransSeq, ige1.LineNum FROM oivl JOIN ige1 ON "
                + relation["condition"]
                + " ORDER BY oivl.TransSeq"
            )
            self.assertEqual(rows.fetchall(), [(1001, 0), (1002, 0), (1004, 1)])

    def test_query_keeps_work_order_scope_and_aggregates_layers_before_transaction_quantities(self) -> None:
        rows = self.issue_query()
        self.assertEqual(len(rows), 4)
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertEqual(issue["component_line_num"], 7)
        self.assertEqual(issue["posting_date"], "2024-05-10")
        self.assertEqual(issue["creation_date"], "2024-05-12")
        self.assertEqual(issue["document_quantity"], 2)
        self.assertEqual(issue["inventory_quantity"], 20)
        self.assertEqual(issue["valuation_transactions"], 2)
        self.assertEqual(issue["valuation_layers"], 3)
        self.assertEqual(issue["valuation_issue_quantity"], 20)
        self.assertEqual(issue["stock_movement_value"], -224)
        self.assertEqual(issue["layer_movement_value"], -224)
        self.assertEqual(issue["issue_cost"], 224)
        self.assertAlmostEqual(issue["effective_unit_cost"], 11.2)
        self.assertAlmostEqual(issue["stored_inventory_unit_price"], 11.2)
        self.assertEqual(issue["minimum_layer_calculation_price"], 10)
        self.assertEqual(issue["maximum_layer_calculation_price"], 12)

    def test_zero_cogs_is_not_a_zero_issue_cost_and_abs_does_not_hide_a_reversal(self) -> None:
        rows = self.issue_query()
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertEqual(issue["source_cogs_value"], 0)
        self.assertEqual(issue["document_stock_sum"], 224)
        self.assertEqual(issue["issue_cost"], 224)
        self.assertNotEqual(issue["issue_cost"], issue["source_line_total"])
        reversal = next(row for row in rows if row["issue_doc_entry"] == 503)
        self.assertEqual(reversal["stock_movement_value"], 24)
        self.assertEqual(reversal["issue_cost"], -24)

    def test_non_inventory_and_incomplete_amounts_remain_visible_without_zero_fallback(self) -> None:
        rows = self.issue_query()
        service = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 1))
        self.assertEqual(service["valuation_transactions"], 0)
        self.assertEqual(service["valuation_status"], "not_inventory_valued")
        unknown = next(row for row in rows if row["issue_doc_entry"] == 501)
        self.assertEqual(unknown["valuation_transactions"], 1)
        self.assertEqual(unknown["valuation_status"], "incomplete_valuation_value")
        for row in (service, unknown):
            self.assertIsNone(row["stock_movement_value"])
            self.assertIsNone(row["layer_movement_value"])
            self.assertIsNone(row["issue_cost"])
            self.assertIsNone(row["effective_unit_cost"])

    def test_partial_null_layers_cannot_be_reported_as_a_complete_layer_amount(self) -> None:
        rows = self.issue_query(
            "UPDATE dbo.IVL1 SET TransValue = NULL WHERE TransSeq = 1001 AND LayerID = 1;"
        )
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertIsNone(issue["layer_movement_value"])
        self.assertEqual(issue["stock_movement_value"], -224)
        rows = self.issue_query("UPDATE dbo.OIVL SET SumStock = NULL WHERE TransSeq = 1001;")
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertIsNone(issue["stock_movement_value"])
        self.assertIsNone(issue["issue_cost"])
        self.assertEqual(issue["valuation_status"], "incomplete_valuation_value")

    def test_inventory_line_without_valuation_is_missing_not_a_confirmed_zero(self) -> None:
        rows = self.issue_query("DELETE FROM dbo.OIVL WHERE TransSeq = 1003;")
        issue = next(row for row in rows if row["issue_doc_entry"] == 501)
        self.assertEqual(issue["valuation_status"], "missing_valuation")
        self.assertIsNone(issue["issue_cost"])

    def test_stored_price_and_effective_price_are_separate_and_zero_quantity_has_no_unit_cost(self) -> None:
        rows = self.issue_query(
            "UPDATE dbo.IGE1 SET StockPrice = 11.2001 WHERE DocEntry = 500 AND LineNum = 0;"
        )
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertAlmostEqual(issue["stored_inventory_unit_price"], 11.2001)
        self.assertAlmostEqual(issue["effective_unit_cost"], 11.2)
        rows = self.issue_query("UPDATE dbo.IGE1 SET InvQty = 0 WHERE DocEntry = 500 AND LineNum = 0;")
        issue = next(row for row in rows if (row["issue_doc_entry"], row["issue_line_num"]) == (500, 0))
        self.assertIsNone(issue["effective_unit_cost"])
        self.assertEqual(issue["issue_cost"], 224)

    def test_official_stock_sum_and_cogs_roles_are_exposed_separately(self) -> None:
        models = {item["name"]: item for item in self.mdl["models"]}
        for name in ("ige1", "ign1"):
            columns = {item["name"]: item for item in models[name]["columns"]}
            self.assertIn("StockSum", columns)
            self.assertEqual(columns["StockValue"]["displayName"], "总销货成本值")
        valuation_columns = {item["name"] for item in models["oivl"]["columns"]}
        self.assertTrue({"InvntAct", "WipAct", "WipVal"} <= valuation_columns)

    def test_approved_source_paths_are_removed_from_deferred_but_other_paths_stay_deferred(self) -> None:
        deferred = read_json(ROOT / "validation" / "deferred.json")
        paths = {(item["from_table"], item["to_table"]) for item in deferred["relationships"]}
        self.assertNotIn(("IGE1", "WOR1"), paths)
        self.assertNotIn(("OIVL", "IGE1"), paths)
        self.assertTrue({("OIVL", "IGN1"), ("OIVL", "WTR1")} <= paths)


if __name__ == "__main__":
    unittest.main()
