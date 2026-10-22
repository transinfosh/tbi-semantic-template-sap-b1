"""Synthetic sales relationship contracts; no company data, network, Frappe, or LLM."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build

DOCUMENTS = (
    ("oqut", "qut1", 23),
    ("ordr", "rdr1", 17),
    ("odln", "dln1", 15),
    ("ordn", "rdn1", 16),
    ("oinv", "inv1", 13),
    ("orin", "rin1", 14),
    ("odpi", "dpi1", 203),
)
SOURCE_PATHS = (
    ("sap_rdr1_qut1", "rdr1", "qut1", 23),
    ("sap_dln1_qut1", "dln1", "qut1", 23),
    ("rdr1_dln1", "dln1", "rdr1", 17),
    ("sap_inv1_qut1", "inv1", "qut1", 23),
    ("sap_inv1_rdr1", "inv1", "rdr1", 17),
    ("dln1_inv1", "inv1", "dln1", 15),
    ("dln1_rdn1", "rdn1", "dln1", 15),
    ("inv1_rin1", "rin1", "inv1", 13),
    ("sap_rin1_rdn1", "rin1", "rdn1", 16),
    ("sap_dpi1_qut1", "dpi1", "qut1", 23),
    ("dpi1_rdr1", "dpi1", "rdr1", 17),
)


class SalesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        mdl = build()
        cls.models = {item["name"]: item for item in mdl["models"]}
        cls.relations = {item["name"]: item for item in mdl["relationships"]}

    def relation_between(self, first: str, second: str) -> dict:
        matches = [
            item for item in self.relations.values() if set(item["models"]) == {first, second}
        ]
        self.assertEqual(len(matches), 1, f"Expected one relationship between {first} and {second}")
        return matches[0]

    def test_document_expenses_preserve_records_types_and_currency_without_item_fanout(self) -> None:
        for expense, header, line in (("inv3", "oinv", "inv1"), ("rin3", "orin", "rin1"), ("pch3", "opch", "pch1"), ("rpc3", "orpc", "rpc1")):
            with self.subTest(expense=expense), closing(sqlite3.connect(":memory:")) as connection:
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, DocCur TEXT, DocTotal NUMERIC);"
                    f"CREATE TABLE {expense} (DocEntry INT, LineNum INT, ExpnsCode INT, "
                    "LineTotal NUMERIC, TotalFrgn NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                    "CREATE TABLE oexd (ExpnsCode INT PRIMARY KEY, ExpnsName TEXT);"
                    f"INSERT INTO {header} VALUES (10, 'USD', 1100), (20, 'EUR', 2200);"
                    f"INSERT INTO {expense} VALUES (10, 4, 1, 100, 14), (10, 8, 1, 20, 3), "
                    "(10, 11, 2, 30, 4), (20, 4, 99, 200, 25);"
                    "INSERT INTO oexd VALUES (1, 'Freight'), (2, 'Insurance');"
                )
                parent = self.relation_between(expense, header)
                types = self.relation_between(expense, "oexd")
                self.assertEqual(parent["joinType"], "MANY_TO_ONE")
                self.assertEqual(types["joinType"], "MANY_TO_ONE")
                joined = (
                    f"FROM {expense} LEFT JOIN {header} ON {parent['condition']} "
                    f"LEFT JOIN oexd ON {types['condition']}"
                )
                by_type = connection.execute(
                    f"SELECT oexd.ExpnsName, SUM({expense}.LineTotal) {joined} "
                    "GROUP BY oexd.ExpnsName ORDER BY oexd.ExpnsName"
                ).fetchall()
                self.assertEqual(by_type, [(None, 200), ("Freight", 120), ("Insurance", 30)])
                by_currency = connection.execute(
                    f"SELECT {header}.DocCur, SUM({expense}.TotalFrgn) {joined} "
                    f"GROUP BY {header}.DocCur ORDER BY {header}.DocCur"
                ).fetchall()
                self.assertEqual(by_currency, [("EUR", 25), ("USD", 21)])
                # A repeated expense code is still a separate record; retain unmatched types.
                self.assertEqual(connection.execute(f"SELECT COUNT(*) {joined}").fetchone()[0], 4)
                self.assertEqual(self.models[expense]["primaryKey"], ["DocEntry", "LineNum"])
                self.assertFalse(any(set(r["models"]) == {expense, line} for r in self.relations.values()))

    def test_formal_quotation_scope_keeps_alternatives_and_confirmation_distinct(self) -> None:
        for model, fields in (("oqut", {"Confirmed"}), ("qut1", {"LineType", "TreeType"})):
            self.assertTrue(fields <= {c["name"] for c in self.models[model]["columns"]})
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                "CREATE TABLE oqut (DocEntry INT PRIMARY KEY, Confirmed TEXT, DocStatus TEXT);"
                "CREATE TABLE qut1 (DocEntry INT, LineNum INT, LineType TEXT, TreeType TEXT, "
                "Quantity NUMERIC, LineTotal NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                "INSERT INTO oqut VALUES (1, 'Y', 'O'), (2, 'N', 'O');"
                "INSERT INTO qut1 VALUES (1, 2, 'R', 'S', 2, 100), "
                "(1, 5, 'R', 'I', 6, 0), (1, 9, 'A', 'N', 2, 180), "
                "(1, 12, '?', 'N', 2, 700), (2, 0, 'R', 'N', 1, 90);"
            )
            joined = f"FROM oqut JOIN qut1 ON {self.relation_between('oqut', 'qut1')['condition']}"
            regular = connection.execute(
                f"SELECT SUM(qut1.LineTotal) {joined} WHERE oqut.Confirmed='Y' AND qut1.LineType='R'"
            ).fetchone()[0]
            alternatives = connection.execute(
                f"SELECT SUM(qut1.LineTotal) {joined} WHERE oqut.Confirmed='Y' AND qut1.LineType='A'"
            ).fetchone()[0]
            roles = connection.execute(
                "SELECT TreeType, SUM(Quantity) FROM qut1 WHERE DocEntry=1 AND LineType='R' "
                "GROUP BY TreeType ORDER BY TreeType"
            ).fetchall()
            self.assertEqual((regular, alternatives), (100, 180))
            self.assertEqual(roles, [("I", 6), ("S", 2)])
            # These are explicit question scopes, not new universal filtering rules.
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM qut1").fetchone()[0], 5)

    def test_service_open_amount_and_reserve_delivery_status_have_separate_roles(self) -> None:
        for header, line, _ in DOCUMENTS:
            self.assertTrue(
                {"OpenSum", "OpenSumFC", "OpenSumSys"}
                <= {c["name"] for c in self.models[line]["columns"]}
            )
        self.assertIn("InvntSttus", {c["name"] for c in self.models["oinv"]["columns"]})
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                "CREATE TABLE oinv (DocEntry INT PRIMARY KEY, DocType TEXT, isIns TEXT, "
                "DocStatus TEXT, InvntSttus TEXT);"
                "CREATE TABLE inv1 (DocEntry INT, LineNum INT, OpenQty NUMERIC, OpenSum NUMERIC);"
                "INSERT INTO oinv VALUES (1, 'S', 'N', 'O', 'C'), "
                "(2, 'I', 'Y', 'C', 'O'), (3, 'I', 'Y', 'C', 'C');"
                "INSERT INTO inv1 VALUES (1, 0, 1, 150), (2, 0, 4, 0), (3, 0, 0, 0);"
            )
            amount = connection.execute(
                "SELECT SUM(inv1.OpenSum) FROM oinv JOIN inv1 "
                f"ON {self.relation_between('oinv', 'inv1')['condition']} WHERE oinv.DocType='S'"
            ).fetchone()[0]
            pending_delivery = connection.execute(
                "SELECT DocEntry FROM oinv WHERE isIns='Y' AND InvntSttus='O'"
            ).fetchall()
            self.assertEqual(amount, 150)
            self.assertEqual(pending_delivery, [(2,)])

    def test_line_projects_and_salespeople_keep_their_own_keys_and_unmatched_rows(self) -> None:
        for header, line, _ in DOCUMENTS:
            with self.subTest(line=line), closing(sqlite3.connect(":memory:")) as connection:
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, Project TEXT, SlpCode INT);"
                    f"CREATE TABLE {line} (DocEntry INT, LineNum INT, Project TEXT, SlpCode INT);"
                    "CREATE TABLE oprj (PrjCode TEXT PRIMARY KEY, PrjName TEXT, Active TEXT);"
                    "CREATE TABLE oslp (SlpCode INT PRIMARY KEY, SlpName TEXT);"
                    f"INSERT INTO {header} VALUES (1, 'HEAD', 8);"
                    f"INSERT INTO {line} VALUES (1, 0, 'LINE', 7), (1, 1, NULL, -1), "
                    "(1, 2, 'MISSING', 99);"
                    "INSERT INTO oprj VALUES ('HEAD', 'Header project', 'Y'), "
                    "('LINE', 'Saved line project', 'N');"
                    "INSERT INTO oslp VALUES (7, 'Line salesperson'), (8, 'Header salesperson');"
                )
                rows = connection.execute(
                    f"SELECT {line}.LineNum, oprj.PrjName, oslp.SlpName FROM {header} "
                    f"JOIN {line} ON {self.relation_between(header, line)['condition']} "
                    f"LEFT JOIN oprj ON {self.relation_between(line, 'oprj')['condition']} "
                    f"LEFT JOIN oslp ON {self.relation_between(line, 'oslp')['condition']} "
                    f"ORDER BY {line}.LineNum"
                ).fetchall()
                self.assertEqual(
                    rows,
                    [(0, "Saved line project", "Line salesperson"), (1, None, None), (2, None, None)],
                )
                header_project = self.relation_between(header, "oprj")
                self.assertEqual(header_project["condition"], f"{header}.Project = oprj.PrjCode")

    def test_drawn_payment_roles_have_saved_currency_families_at_their_own_grain(self) -> None:
        for model in ("inv9", "rin9", "inv11", "rin11"):
            columns = {c["name"]: c for c in self.models[model]["columns"]}
            families = (
                [("ApplDrawn", "ApplDrawnF", "ApplDrawnS"), ("Vat", "VatFc", "VatSc")]
                if model.endswith("9")
                else [
                    ("LineTotal", "TotalFrgn", "TotalSumSy"),
                    ("VatSum", "VatSumFrgn", "VatSumSys"),
                    ("ApplNet", "ApplNetFc", "ApplNetSc"),
                    ("ApplVat", "ApplVatFc", "ApplVatSc"),
                    ("ApplGross", "ApplGrossF", "ApplGrossS"),
                    ("BaseNet", "BaseNetFc", "BaseNetSc"),
                    ("BaseVat", "BaseVatFc", "BaseVatSc"),
                    ("BaseGross", "BaseGrossF", "BaseGrossS"),
                ]
            )
            for family in families:
                with self.subTest(model=model, family=family):
                    for field in family:
                        self.assertTrue(columns[field]["type"].startswith("DECIMAL"))
            self.assertEqual(
                self.models[model]["primaryKey"],
                ["DocEntry", "LineNum", "LineSeq"] if model.endswith("11") else ["DocEntry", "LineNum"],
            )

    def condition(self, name: str) -> str:
        return self.relations[name]["condition"]

    def test_core_amount_roles_keep_complete_numeric_currency_families(self) -> None:
        header_families = (
            ("DocTotal", "DocTotalFC", "DocTotalSy"),
            ("VatSum", "VatSumFC", "VatSumSy"),
            ("DiscSum", "DiscSumFC", "DiscSumSy"),
            ("TotalExpns", "TotalExpFC", "TotalExpSC"),
            ("RoundDif", "RoundDifFC", "RoundDifSy"),
        )
        line_families = (
            ("LineTotal", "TotalFrgn", "TotalSumSy"),
            ("VatSum", "VatSumFrgn", "VatSumSy"),
            ("GTotal", "GTotalFC", "GTotalSC"),
        )
        # The explicit field families are a coverage contract, not a suffix-based currency inference.
        for header, line, _ in DOCUMENTS:
            for model_name, families in ((header, header_families), (line, line_families)):
                columns = {column["name"]: column for column in self.models[model_name]["columns"]}
                for family in families:
                    with self.subTest(model=model_name, family=family):
                        self.assertTrue(set(family) <= columns.keys(), f"Missing amount role in {model_name}")
                        for field in family:
                            self.assertIn(
                                columns[field]["type"].upper().split("(")[0], {"DECIMAL", "NUMERIC"}
                            )

    def test_all_declared_source_paths_keep_type_document_and_line_identity(self) -> None:
        for name, child, source, source_type in SOURCE_PATHS:
            with self.subTest(relationship=name), closing(sqlite3.connect(":memory:")) as connection:
                relation = self.relations[name]
                expected_cardinality = (
                    "MANY_TO_ONE" if relation["models"] == [child, source] else "ONE_TO_MANY"
                )
                self.assertEqual(relation["joinType"], expected_cardinality)
                connection.executescript(
                    f"CREATE TABLE {source} (DocEntry INT, LineNum INT, ItemCode TEXT, "
                    "PRIMARY KEY (DocEntry, LineNum));"
                    f"CREATE TABLE {child} (DocEntry INT, LineNum INT, BaseEntry INT, "
                    "BaseLine INT, BaseType INT, ItemCode TEXT, PRIMARY KEY (DocEntry, LineNum));"
                    f"INSERT INTO {source} VALUES "
                    "(100, 0, 'SAME-ITEM'), (100, 1, 'SAME-ITEM'), (200, 0, 'SAME-ITEM');"
                )
                connection.executemany(
                    f"INSERT INTO {child} VALUES (?, ?, ?, ?, ?, ?)",
                    [
                        (1, 7, 100, 1, source_type, "SAME-ITEM"),
                        (2, 7, 100, 1, 999, "SAME-ITEM"),
                        (3, 7, 100, 2, source_type, "SAME-ITEM"),
                        (4, 7, 200, 0, source_type, "SAME-ITEM"),
                        (5, 7, None, None, -1, "SAME-ITEM"),
                    ],
                )
                rows = connection.execute(
                    f"SELECT {child}.DocEntry, {source}.DocEntry, {source}.LineNum "
                    f"FROM {child} JOIN {source} ON {relation['condition']} ORDER BY {child}.DocEntry"
                ).fetchall()
                self.assertEqual(rows, [(1, 100, 1), (4, 200, 0)])

    def test_seven_document_groups_have_complete_standard_dimensions(self) -> None:
        for header, line, _ in DOCUMENTS:
            with self.subTest(header=header):
                head_line = self.relation_between(header, line)
                self.assertEqual(head_line["models"], [header, line])
                self.assertEqual(head_line["joinType"], "ONE_TO_MANY")
                for source, dimension in (
                    (header, "ocrd"),
                    (header, "oslp"),
                    (header, "nnm1"),
                    (line, "oitm"),
                    (line, "owhs"),
                    (line, "oact"),
                ):
                    relation = self.relation_between(source, dimension)
                    self.assertEqual(relation["models"], [source, dimension])
                    self.assertEqual(relation["joinType"], "MANY_TO_ONE")

    def test_document_salesperson_is_not_the_customers_current_salesperson(self) -> None:
        for header, _, _ in DOCUMENTS:
            with self.subTest(header=header), closing(sqlite3.connect(":memory:")) as connection:
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, CardCode TEXT, SlpCode INT);"
                    "CREATE TABLE ocrd (CardCode TEXT PRIMARY KEY, SlpCode INT);"
                    "CREATE TABLE oslp (SlpCode INT PRIMARY KEY, SlpName TEXT);"
                    f"INSERT INTO {header} VALUES (1, 'C001', 7);"
                    "INSERT INTO ocrd VALUES ('C001', 8);"
                    "INSERT INTO oslp VALUES (7, 'Document salesperson'), (8, 'Current BP salesperson');"
                )
                rows = connection.execute(
                    f"SELECT {header}.DocEntry, oslp.SlpName FROM {header} "
                    f"JOIN ocrd ON {self.relation_between(header, 'ocrd')['condition']} "
                    f"JOIN oslp ON {self.relation_between(header, 'oslp')['condition']}"
                ).fetchall()
                self.assertEqual(rows, [(1, "Document salesperson")])

    def test_number_series_keeps_document_type_and_does_not_join_by_display_number(self) -> None:
        for header, _, object_type in DOCUMENTS:
            with self.subTest(header=header), closing(sqlite3.connect(":memory:")) as connection:
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, DocNum INT, Series INT, ObjType TEXT);"
                    "CREATE TABLE nnm1 (Series INT PRIMARY KEY, ObjectCode TEXT, SeriesName TEXT);"
                )
                connection.executemany(
                    f"INSERT INTO {header} VALUES (?, ?, ?, ?)",
                    [(1, 700, 100, str(object_type)), (2, 700, 101, str(object_type))],
                )
                connection.executemany(
                    "INSERT INTO nnm1 VALUES (?, ?, ?)",
                    [(100, str(object_type), "Correct series"), (101, "999", "Other document type")],
                )
                rows = connection.execute(
                    f"SELECT {header}.DocEntry, nnm1.SeriesName FROM {header} "
                    f"JOIN nnm1 ON {self.relation_between(header, 'nnm1')['condition']}"
                ).fetchall()
                self.assertEqual(rows, [(1, "Correct series")])

    def test_header_amount_is_counted_at_document_grain_after_line_filters(self) -> None:
        for header, line, _ in DOCUMENTS:
            with self.subTest(header=header), closing(sqlite3.connect(":memory:")) as connection:
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, DocTotal NUMERIC);"
                    f"CREATE TABLE {line} (DocEntry INT, LineNum INT, LineTotal NUMERIC, "
                    "PRIMARY KEY (DocEntry, LineNum));"
                    f"INSERT INTO {header} VALUES (1, 100), (2, 100);"
                    f"INSERT INTO {line} VALUES (1, 0, 40), (1, 1, 60), (2, 0, 100);"
                )
                joined = f"FROM {header} JOIN {line} ON {self.relation_between(header, line)['condition']}"
                naive = connection.execute(f"SELECT SUM({header}.DocTotal) {joined}").fetchone()[0]
                distinct_amount = connection.execute(
                    f"SELECT SUM(DISTINCT {header}.DocTotal) {joined}"
                ).fetchone()[0]
                correct = connection.execute(
                    f"SELECT SUM(DocTotal) FROM (SELECT {header}.DocEntry, {header}.DocTotal "
                    f"{joined} GROUP BY {header}.DocEntry, {header}.DocTotal)"
                ).fetchone()[0]
                self.assertEqual(naive, 300)
                self.assertEqual(distinct_amount, 100)
                self.assertEqual(correct, 200)

    def test_partial_deliveries_and_invoice_return_branches_aggregate_before_combining(self) -> None:
        with closing(sqlite3.connect(":memory:")) as connection:
            connection.executescript(
                "CREATE TABLE rdr1 (DocEntry INT, LineNum INT, Quantity NUMERIC, "
                "PRIMARY KEY (DocEntry, LineNum));"
                "CREATE TABLE dln1 (DocEntry INT, LineNum INT, BaseEntry INT, BaseLine INT, "
                "BaseType INT, Quantity NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                "CREATE TABLE inv1 (DocEntry INT, LineNum INT, BaseEntry INT, BaseLine INT, "
                "BaseType INT, Quantity NUMERIC, LineTotal NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                "CREATE TABLE rdn1 (DocEntry INT, LineNum INT, BaseEntry INT, BaseLine INT, "
                "BaseType INT, Quantity NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                "INSERT INTO rdr1 VALUES (100, 0, 10), (100, 1, 4), (101, 0, 99);"
                "INSERT INTO dln1 VALUES "
                "(200, 0, 100, 0, 17, 6), (201, 0, 100, 0, 17, 4), (202, 0, 101, 0, 17, 99);"
                "INSERT INTO inv1 VALUES "
                "(300, 0, 200, 0, 15, 2, 20), (301, 0, 200, 0, 15, 4, 40), "
                "(302, 0, 201, 0, 15, 4, 40), (303, 0, 100, 1, 17, 4, 40), "
                "(304, 0, 200, 0, 17, 70, 700);"
                "INSERT INTO rdn1 VALUES (400, 0, 200, 0, 15, 1), (401, 0, 200, 0, 15, 1);"
            )
            order_delivery = self.condition("rdr1_dln1")
            delivery_invoice = self.condition("dln1_inv1")
            delivery_return = self.condition("dln1_rdn1")
            direct_invoice = self.condition("sap_inv1_rdr1")
            naive = connection.execute(
                "SELECT SUM(dln1.Quantity), SUM(inv1.Quantity) FROM rdr1 "
                f"JOIN dln1 ON {order_delivery} LEFT JOIN inv1 ON {delivery_invoice} "
                f"LEFT JOIN rdn1 ON {delivery_return} WHERE rdr1.DocEntry = 100"
            ).fetchone()
            self.assertEqual(naive, (28, 16))
            # This example reports separate business facts; it does not define a net-sales policy.
            rows = connection.execute(
                "WITH delivered AS ("
                "SELECT rdr1.DocEntry, rdr1.LineNum, SUM(dln1.Quantity) AS qty FROM rdr1 "
                f"JOIN dln1 ON {order_delivery} GROUP BY rdr1.DocEntry, rdr1.LineNum), "
                "invoice_sources AS ("
                "SELECT rdr1.DocEntry, rdr1.LineNum, inv1.Quantity, inv1.LineTotal FROM rdr1 "
                f"JOIN dln1 ON {order_delivery} JOIN inv1 ON {delivery_invoice} "
                "UNION ALL "
                "SELECT rdr1.DocEntry, rdr1.LineNum, inv1.Quantity, inv1.LineTotal FROM rdr1 "
                f"JOIN inv1 ON {direct_invoice}), "
                "invoiced AS (SELECT DocEntry, LineNum, SUM(Quantity) AS qty, SUM(LineTotal) AS amount "
                "FROM invoice_sources GROUP BY DocEntry, LineNum), "
                "returned AS ("
                "SELECT rdr1.DocEntry, rdr1.LineNum, SUM(rdn1.Quantity) AS qty FROM rdr1 "
                f"JOIN dln1 ON {order_delivery} JOIN rdn1 ON {delivery_return} "
                "GROUP BY rdr1.DocEntry, rdr1.LineNum) "
                "SELECT rdr1.LineNum, delivered.qty, invoiced.qty, invoiced.amount, returned.qty "
                "FROM rdr1 LEFT JOIN delivered USING (DocEntry, LineNum) "
                "LEFT JOIN invoiced USING (DocEntry, LineNum) LEFT JOIN returned USING (DocEntry, LineNum) "
                "WHERE rdr1.DocEntry = 100 ORDER BY rdr1.LineNum"
            ).fetchall()
            self.assertEqual(rows, [(0, 10, 10, 100, 2), (1, None, 4, 40, None)])

    def test_drawn_amounts_and_detail_sequences_are_not_multiplied_by_product_lines(self) -> None:
        for header, line, draw, detail in (
            ("oinv", "inv1", "inv9", "inv11"),
            ("orin", "rin1", "rin9", "rin11"),
        ):
            with self.subTest(header=header), closing(sqlite3.connect(":memory:")) as connection:
                self.assertEqual(self.models[draw]["primaryKey"], ["DocEntry", "LineNum"])
                self.assertEqual(self.models[detail]["primaryKey"], ["DocEntry", "LineNum", "LineSeq"])
                for bridge in (draw, detail):
                    self.assertFalse(
                        any(set(r["models"]) == {bridge, line} for r in self.relations.values())
                    )
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY);"
                    f"CREATE TABLE {line} (DocEntry INT, LineNum INT, PRIMARY KEY (DocEntry, LineNum));"
                    f"CREATE TABLE {draw} (DocEntry INT, LineNum INT, DrawnSum NUMERIC, "
                    "PRIMARY KEY (DocEntry, LineNum));"
                    f"CREATE TABLE {detail} (DocEntry INT, LineNum INT, LineSeq INT, Gross NUMERIC, "
                    "PRIMARY KEY (DocEntry, LineNum, LineSeq));"
                    f"INSERT INTO {header} VALUES (1);"
                    f"INSERT INTO {line} VALUES (1, 0), (1, 1);"
                    f"INSERT INTO {draw} VALUES (1, 0, 30), (1, 1, 20);"
                    f"INSERT INTO {detail} VALUES (1, 0, 0, 20), (1, 0, 1, 10), (1, 1, 0, 20);"
                )
                joins = (
                    f"FROM {header} JOIN {line} ON {self.relation_between(header, line)['condition']} "
                    f"JOIN {draw} ON {self.relation_between(draw, header)['condition']} "
                    f"JOIN {detail} ON {self.relation_between(detail, header)['condition']}"
                )
                naive = connection.execute(
                    f"SELECT COUNT(*), SUM({draw}.DrawnSum), SUM({detail}.Gross) {joins}"
                ).fetchone()
                self.assertEqual(naive, (12, 300, 200))
                rows = connection.execute(
                    f"WITH draw_totals AS (SELECT DocEntry, SUM(DrawnSum) AS amount FROM {draw} "
                    "GROUP BY DocEntry), detail_totals AS ("
                    f"SELECT DocEntry, SUM(Gross) AS amount FROM {detail} GROUP BY DocEntry) "
                    f"SELECT {header}.DocEntry, draw_totals.amount, detail_totals.amount "
                    f"FROM {header} LEFT JOIN draw_totals USING (DocEntry) "
                    "LEFT JOIN detail_totals USING (DocEntry)"
                ).fetchall()
                self.assertEqual(rows, [(1, 50, 50)])

    def test_approved_down_payment_bridges_keep_their_own_type_discriminator(self) -> None:
        for bridge, discriminator, field_type, accepted, rejected in (
            ("inv9", "ObjType", "TEXT", "203", "204"),
            ("inv11", "BaseType", "INT", 203, 204),
            ("rin11", "BaseType", "INT", 203, 204),
        ):
            with self.subTest(bridge=bridge), closing(sqlite3.connect(":memory:")) as connection:
                relation = self.relation_between(bridge, "odpi")
                connection.executescript(
                    "CREATE TABLE odpi (DocEntry INT PRIMARY KEY);"
                    f"CREATE TABLE {bridge} (DocEntry INT, LineNum INT, BaseAbs INT, "
                    f"{discriminator} {field_type});"
                    "INSERT INTO odpi VALUES (500);"
                )
                connection.executemany(
                    f"INSERT INTO {bridge} VALUES (?, ?, ?, ?)",
                    [(1, 0, 500, accepted), (1, 1, 500, rejected)],
                )
                rows = connection.execute(
                    f"SELECT {bridge}.LineNum, odpi.DocEntry FROM {bridge} JOIN odpi "
                    f"ON {relation['condition']}"
                ).fetchall()
                self.assertEqual(rows, [(0, 500)])

    def test_service_rows_keep_their_document_description_without_an_item_match(self) -> None:
        for header, line, _ in DOCUMENTS:
            with self.subTest(header=header), closing(sqlite3.connect(":memory:")) as connection:
                header_fields = {c["name"] for c in self.models[header]["columns"]}
                line_fields = {c["name"] for c in self.models[line]["columns"]}
                self.assertIn("DocType", header_fields)
                self.assertTrue({"Dscription", "AcctCode"} <= line_fields)
                connection.executescript(
                    f"CREATE TABLE {header} (DocEntry INT PRIMARY KEY, DocType TEXT);"
                    f"CREATE TABLE {line} (DocEntry INT, LineNum INT, ItemCode TEXT, Dscription TEXT, "
                    "AcctCode TEXT, LineTotal NUMERIC, PRIMARY KEY (DocEntry, LineNum));"
                    "CREATE TABLE oitm (ItemCode TEXT PRIMARY KEY, ItemName TEXT);"
                    "CREATE TABLE oact (AcctCode TEXT PRIMARY KEY, AcctName TEXT);"
                    f"INSERT INTO {header} VALUES (1, 'S');"
                    f"INSERT INTO {line} VALUES (1, 0, NULL, 'Contract service description', '4000', 25);"
                    "INSERT INTO oitm VALUES ('OTHER', 'Current master name');"
                    "INSERT INTO oact VALUES ('4000', 'Selected service account');"
                )
                rows = connection.execute(
                    f"SELECT {header}.DocType, {line}.Dscription, {line}.AcctCode, "
                    f"{line}.LineTotal, oitm.ItemName, oact.AcctName FROM {header} "
                    f"JOIN {line} ON {self.relation_between(header, line)['condition']} "
                    f"LEFT JOIN oitm ON {self.relation_between(line, 'oitm')['condition']} "
                    f"LEFT JOIN oact ON {self.relation_between(line, 'oact')['condition']}"
                ).fetchall()
                self.assertEqual(
                    rows,
                    [("S", "Contract service description", "4000", 25, None, "Selected service account")],
                )


if __name__ == "__main__":
    unittest.main()
