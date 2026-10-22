"""Exercise the actual workspace View SQL with synthetic branching and identity collisions."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "validation" / "workspace-views"
spec = importlib.util.spec_from_file_location(
    "workspace_view_pack", PACK_ROOT / "load_pack.py"
)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class WorkspaceViewsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pack = loader.load_pack()
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        models = [json.loads(p.read_text()) for p in (ROOT / "models").glob("*.json")]
        for model in models + self.pack["models"]:
            columns = ",".join(f'"{c["name"]}" {c["type"]}' for c in model["columns"])
            self.db.execute(f'CREATE TABLE "{model["name"]}" ({columns})')
        for view in self.pack["views"]:
            self.db.execute(f'CREATE VIEW "{view["name"]}" AS {view["statement"]}')
        self.addCleanup(self.db.close)

    def put(self, table: str, **values) -> None:
        names = ",".join(f'"{name}"' for name in values)
        params = ",".join("?" for _ in values)
        self.db.execute(
            f'INSERT INTO "{table}" ({names}) VALUES ({params})', list(values.values())
        )

    def test_current_batch_serial_balances_expose_units_without_changing_quantities(
        self,
    ):
        self.put("oitm", ItemCode="BATCH-ITEM", InvntryUom="KG")
        self.put("oitm", ItemCode="SERIAL-ITEM", InvntryUom="EA")
        self.put("owhs", WhsCode="W")
        self.put("obin", AbsEntry=1, BinCode="BIN", WhsCode="W")
        self.put(
            "obtn", AbsEntry=11, ItemCode="BATCH-ITEM", SysNumber=1, DistNumber="B"
        )
        self.put(
            "osrn", AbsEntry=11, ItemCode="SERIAL-ITEM", SysNumber=1, DistNumber="S"
        )
        for table, item, qty in (
            ("obbq", "BATCH-ITEM", 12.5),
            ("osbq", "SERIAL-ITEM", 1),
        ):
            self.put(
                table,
                AbsEntry=1,
                ItemCode=item,
                SnBMDAbs=11,
                BinAbs=1,
                WhsCode="W",
                OnHandQty=qty,
            )
        for table, item, qty in (
            ("obtq", "BATCH-ITEM", 12.5),
            ("osrq", "SERIAL-ITEM", 1),
        ):
            self.put(
                table,
                AbsEntry=1,
                ItemCode=item,
                SysNumber=1,
                MdAbsEntry=11,
                WhsCode="W",
                Quantity=qty,
            )
        for view in (
            "inventory_batch_serial_bin_current_balance",
            "inventory_batch_serial_warehouse_current_balance",
        ):
            with self.subTest(view=view):
                rows = self.rows(view)
                self.assertEqual(len(rows), 2)
                self.assertEqual(
                    {
                        r["item_code"]: (
                            r["on_hand_quantity"],
                            r["current_inventory_unit"],
                        )
                        for r in rows
                    },
                    {"BATCH-ITEM": (12.5, "KG"), "SERIAL-ITEM": (1, "EA")},
                )
                self.assertEqual(
                    len({(r["management_type"], r["balance_entry"]) for r in rows}), 2
                )

    def rows(self, view: str) -> list[dict]:
        return [dict(row) for row in self.db.execute(f'SELECT * FROM "{view}"')]

    def test_every_view_binds_against_portable_models_and_has_business_titles(
        self,
    ) -> None:
        self.assertEqual(len(self.pack["views"]), 16)
        for view in self.pack["views"]:
            with self.subTest(view=view["name"]):
                result = self.db.execute(f'SELECT * FROM "{view["name"]}" LIMIT 0')
                self.assertEqual(
                    [c[0] for c in result.description], list(view["columnTitles"])
                )
                self.assertTrue(all(view["columnTitles"].values()))

    def test_sales_split_deliveries_invoices_and_receipts_preserve_paths_without_amounts(
        self,
    ) -> None:
        self.put("ordr", DocEntry=1, DocNum=7001)
        self.put("rdr1", DocEntry=1, LineNum=0, ItemCode="A", Quantity=10)
        for entry in (10, 11):
            self.put("odln", DocEntry=entry)
            self.put(
                "dln1", DocEntry=entry, LineNum=3, BaseType=17, BaseEntry=1, BaseLine=0
            )
        for entry, delivery in ((20, 10), (21, 10), (22, 11)):
            self.put("oinv", DocEntry=entry)
            self.put(
                "inv1",
                DocEntry=entry,
                LineNum=4,
                BaseType=15,
                BaseEntry=delivery,
                BaseLine=3,
            )
        self.put("orct", DocEntry=30, DocNum=9000)
        self.put("orct", DocEntry=31, DocNum=9001)
        for parent, app in ((30, 0), (31, 2)):
            self.put(
                "rct2",
                DocNum=parent,
                InvoiceId=app,
                InvType=13,
                DocEntry=20,
                SumApplied=40,
            )
        rows = self.rows("sales_order_to_cash_trace")
        self.assertEqual(len(rows), 4)
        self.assertEqual({r["invoice_entry"] for r in rows}, {20, 21, 22})
        self.assertEqual(
            {r["payment_no"] for r in rows if r["payment_entry"]}, {9000, 9001}
        )
        self.assertFalse(
            any("amount" in field or "quantity" in field for field in rows[0])
        )

    def test_direct_reserve_and_unfinished_orders_do_not_invent_delivery_or_duplicate_placeholders(
        self,
    ) -> None:
        for entry in (1, 2, 3):
            self.put("ordr", DocEntry=entry)
            self.put("rdr1", DocEntry=entry, LineNum=0, ItemCode="SAME")
        for invoice, order in ((10, 1), (11, 2)):
            self.put("oinv", DocEntry=invoice, isIns="Y" if order == 2 else "N")
            self.put(
                "inv1",
                DocEntry=invoice,
                LineNum=7,
                BaseType=17,
                BaseEntry=order,
                BaseLine=0,
            )
        self.put("odln", DocEntry=20)
        self.put("dln1", DocEntry=20, LineNum=9, BaseType=13, BaseEntry=11, BaseLine=7)
        rows = {r["order_entry"]: r for r in self.rows("sales_order_to_cash_trace")}
        self.assertEqual(len(self.rows("sales_order_to_cash_trace")), 3)
        self.assertIsNone(rows[1]["logistics_entry"])
        self.assertEqual(rows[2]["path_kind"], "order_invoice_logistics")
        self.assertEqual(rows[2]["logistics_entry"], 20)
        self.assertIsNone(rows[3]["invoice_entry"])

    def test_source_type_and_original_line_prevent_same_item_and_cross_object_collisions(
        self,
    ) -> None:
        self.put("ordr", DocEntry=1)
        for line in (0, 7):
            self.put("rdr1", DocEntry=1, LineNum=line, ItemCode="A")
        self.put("dln1", DocEntry=10, LineNum=2, BaseType=17, BaseEntry=1, BaseLine=7)
        self.put("dln1", DocEntry=11, LineNum=0, BaseType=23, BaseEntry=1, BaseLine=0)
        self.put("inv1", DocEntry=20, LineNum=1, BaseType=15, BaseEntry=10, BaseLine=2)
        rows = self.rows("sales_order_to_cash_trace")
        self.assertEqual(len(rows), 2)
        self.assertEqual(
            next(r for r in rows if r["order_line"] == 7)["invoice_entry"], 20
        )
        self.assertIsNone(
            next(r for r in rows if r["order_line"] == 0)["logistics_entry"]
        )

    def test_receipt_application_not_multiplied_by_invoice_lines_or_other_object_types(
        self,
    ) -> None:
        self.put("oinv", DocEntry=20, DocCur="EUR", DocTotal=200, PaidToDate=100)
        for line in (0, 1, 2):
            self.put("inv1", DocEntry=20, LineNum=line)
        self.put("orct", DocEntry=30, DocNum=500, DocCurr="USD", Canceled="Y")
        self.put("orct", DocEntry=500, DocNum=30, DocCurr="WRONG")
        self.put(
            "rct2",
            DocNum=30,
            InvoiceId=0,
            InvType=13,
            DocEntry=20,
            SumApplied=80,
            AppliedFC=10,
        )
        self.put("rct2", DocNum=30, InvoiceId=1, InvType=14, DocEntry=20, SumApplied=99)
        rows = self.rows("sales_invoice_receipt_applications")
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            (
                rows[0]["payment_no"],
                rows[0]["invoice_currency"],
                rows[0]["payment_currency"],
            ),
            (500, "EUR", "USD"),
        )
        self.assertEqual(rows[0]["payment_cancellation"], "Y")
        self.assertEqual(rows[0]["applied_amount_lc"], 80)
        self.assertEqual(len(self.rows("sales_invoice_current_balance")), 1)
        self.assertEqual(
            self.rows("sales_invoice_current_balance")[0]["current_open_amount_lc"], 100
        )

    def test_purchase_trace_and_payment_internal_keys_use_purchase_object_types(
        self,
    ) -> None:
        self.put("opor", DocEntry=1)
        self.put("por1", DocEntry=1, LineNum=5)
        self.put("pdn1", DocEntry=10, LineNum=7, BaseType=22, BaseEntry=1, BaseLine=5)
        self.put("opch", DocEntry=20)
        self.put("pch1", DocEntry=20, LineNum=0, BaseType=20, BaseEntry=10, BaseLine=7)
        self.put("ovpm", DocEntry=30, DocNum=999)
        self.put("vpm2", DocNum=30, InvoiceId=0, InvType=18, DocEntry=20, SumApplied=50)
        self.put(
            "vpm2", DocNum=30, InvoiceId=1, InvType=13, DocEntry=20, SumApplied=500
        )
        row = self.rows("purchase_order_to_payment_trace")[0]
        self.assertEqual(
            (row["order_line"], row["logistics_line"], row["payment_no"]), (5, 7, 999)
        )
        self.assertEqual(
            self.rows("purchase_invoice_payment_applications")[0]["applied_amount_lc"],
            50,
        )

    def test_one_invoice_for_two_orders_does_not_allocate_one_receipt_twice(
        self,
    ) -> None:
        self.put("oinv", DocEntry=20)
        for order in (1, 2):
            self.put("ordr", DocEntry=order)
            self.put("rdr1", DocEntry=order, LineNum=0)
            self.put(
                "inv1",
                DocEntry=20,
                LineNum=order,
                BaseType=17,
                BaseEntry=order,
                BaseLine=0,
            )
        self.put("orct", DocEntry=30, DocNum=1000)
        self.put(
            "rct2", DocNum=30, InvoiceId=0, InvType=13, DocEntry=20, SumApplied=100
        )
        paths = self.rows("sales_order_to_cash_trace")
        applications = self.rows("sales_invoice_receipt_applications")
        self.assertEqual({r["order_entry"] for r in paths}, {1, 2})
        self.assertEqual({r["payment_entry"] for r in paths}, {30})
        self.assertEqual(len(applications), 1)
        self.assertEqual(sum(r["applied_amount_lc"] for r in applications), 100)

    def test_purchase_reserve_invoice_can_precede_multiple_receipts(self) -> None:
        self.put("opor", DocEntry=1)
        self.put("por1", DocEntry=1, LineNum=5)
        self.put("opch", DocEntry=20, isIns="Y")
        self.put("pch1", DocEntry=20, LineNum=7, BaseType=22, BaseEntry=1, BaseLine=5)
        for entry in (30, 31):
            self.put(
                "pdn1", DocEntry=entry, LineNum=0, BaseType=18, BaseEntry=20, BaseLine=7
            )
        rows = self.rows("purchase_order_to_payment_trace")
        self.assertEqual(len(rows), 2)
        self.assertEqual({r["logistics_entry"] for r in rows}, {30, 31})
        self.assertTrue(all(r["path_kind"] == "order_invoice_logistics" for r in rows))

    def test_batch_serial_master_collisions_and_commitment_logs_do_not_duplicate_stock(
        self,
    ) -> None:
        self.put("odln", DocEntry=10)
        self.put("dln1", DocEntry=10, LineNum=0, ItemCode="A")
        self.put("obtn", AbsEntry=1, ItemCode="A", SysNumber=7, DistNumber="批次甲")
        self.put("obtn", AbsEntry=2, ItemCode="OTHER", SysNumber=7, DistNumber="WRONG")
        self.put("osrn", AbsEntry=1, ItemCode="A", SysNumber=7, DistNumber="SERIAL")
        for log, effect in ((100, 1), (101, 2)):
            self.put(
                "oitl",
                LogEntry=log,
                ItemCode="A",
                ManagedBy=10000044,
                DocType=15,
                DocEntry=10,
                DocLine=0,
                StockEff=effect,
            )
            self.put("itl1", LogEntry=log, ItemCode="A", SysNumber=7, Quantity=-5)
        self.put(
            "oitl",
            LogEntry=102,
            ItemCode="A",
            ManagedBy=10000045,
            DocType=59,
            DocEntry=10,
            DocLine=0,
            StockEff=1,
        )
        self.put("itl1", LogEntry=102, ItemCode="A", SysNumber=7, Quantity=1)
        rows = self.rows("sales_delivery_batch_serial_detail")
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            (rows[0]["batch_serial_number"], rows[0]["signed_inventory_quantity"]),
            ("批次甲", -5),
        )
        self.assertEqual(
            {
                r["batch_serial_number"]
                for r in self.rows("inventory_batch_serial_movements")
            },
            {"批次甲", "SERIAL"},
        )

    def test_two_batches_in_two_bins_preserve_exact_allocations_and_missing_master(
        self,
    ) -> None:
        self.put(
            "oilm",
            MessageID=50,
            ItemCode="A",
            SnBType=10000044,
            ActionType=2,
            AccumType=1,
        )
        self.put("obtn", AbsEntry=1, ItemCode="A", DistNumber="B1")
        self.put("obtn", AbsEntry=2, ItemCode="A", DistNumber="B2")
        for entry in (1, 2):
            self.put("obin", AbsEntry=entry, BinCode=f"BIN-{entry}")
        for entry, master, bin_id, quantity in (
            (1, 1, 1, 3),
            (2, 1, 2, 4),
            (3, 2, 2, 5),
            (4, -1, -1, 2),
        ):
            self.put(
                "obtl",
                AbsEntry=entry,
                MessageID=50,
                SnBMDAbs=master,
                BinAbs=bin_id,
                Quantity=quantity,
            )
        rows = self.rows("inventory_bin_movements")
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(r["raw_bin_quantity"] for r in rows), 14)
        self.assertTrue(all(r["movement_direction"] == "out" for r in rows))
        self.assertEqual(sum(r["batch_serial_number"] is None for r in rows), 1)

    def test_current_bin_totals_are_separate_from_batch_serial_components(self) -> None:
        self.put("oibq", AbsEntry=1, ItemCode="A", BinAbs=10, OnHandQty=8)
        self.put("obbq", AbsEntry=1, ItemCode="A", BinAbs=10, SnBMDAbs=1, OnHandQty=5)
        self.put("osbq", AbsEntry=1, ItemCode="B", BinAbs=10, SnBMDAbs=1, OnHandQty=1)
        totals = self.rows("inventory_bin_current_balance")
        parts = self.rows("inventory_batch_serial_bin_current_balance")
        self.assertEqual([r["on_hand_quantity"] for r in totals], [8])
        self.assertEqual(len(parts), 2)
        self.assertEqual(
            len({(r["management_type"], r["balance_entry"]) for r in parts}), 2
        )

    def test_production_uses_shared_inventory_documents_and_retains_receipt_roles(
        self,
    ) -> None:
        self.put("owor", DocEntry=1, DocNum=7001, Type="D")
        self.put("wor1", DocEntry=1, LineNum=7, ItemCode="COMPONENT")
        self.put("oige", DocEntry=10, DocDate="2023-01-01")
        self.put("oign", DocEntry=11)
        self.put(
            "ige1",
            DocEntry=10,
            LineNum=0,
            BaseType=202,
            BaseEntry=1,
            BaseLine=7,
            Quantity=-2,
        )
        self.put("ige1", DocEntry=10, LineNum=1, BaseType=17, BaseEntry=1, BaseLine=7)
        self.put(
            "ign1", DocEntry=11, LineNum=0, BaseType=202, BaseEntry=1, TranType="R"
        )
        rows = self.rows("production_issue_detail")
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            (
                rows[0]["source_component_line"],
                rows[0]["component_code"],
                rows[0]["document_quantity"],
            ),
            (7, "COMPONENT", -2),
        )
        self.assertEqual(
            self.rows("production_receipt_detail")[0]["receipt_transaction_type"], "R"
        )

    def test_journal_composite_identity_and_negative_debits_survive(self) -> None:
        self.put("oact", AcctCode="INTERNAL", FormatCode="DISPLAY", AcctName="Name")
        for entry, debit in ((1, -5), (2, 7)):
            self.put("ojdt", TransId=entry)
            self.put(
                "jdt1",
                TransId=entry,
                Line_ID=0,
                Account="INTERNAL",
                Debit=debit,
                Credit=0,
            )
        rows = self.rows("finance_journal_line_detail")
        self.assertEqual(len(rows), 2)
        self.assertEqual(sum(r["net_debit_lc"] for r in rows), 2)
        self.assertTrue(all(r["account_display_code"] == "DISPLAY" for r in rows))

    def test_journal_header_and_line_dates_keep_distinct_business_roles(self) -> None:
        # SAP permits independent row posting dates when row editing is enabled.
        self.put("oact", AcctCode="A", FormatCode="A", AcctName="Account")
        for entry in (1, 2):
            self.put(
                "ojdt",
                TransId=entry,
                RefDate="2026-09-30",
                TaxDate="2026-09-29",
                DueDate="2026-10-10",
            )
            for line, debit, credit in ((0, 100, 0), (1, 0, 100)):
                different = entry == 2 and line == 0
                self.put(
                    "jdt1",
                    TransId=entry,
                    Line_ID=line,
                    Account="A",
                    Debit=debit,
                    Credit=credit,
                    RefDate="2026-10-01" if different else "2026-09-30",
                    TaxDate="2026-10-02" if different else "2026-09-29",
                    DueDate="2026-11-15" if different else "2026-10-10",
                )
        rows = self.rows("finance_journal_line_detail")
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            len({(r["journal_entry"], r["journal_line"]) for r in rows}), 4
        )
        for row in rows:
            self.assertEqual(
                (row["posting_date"], row["document_date"], row["due_date"]),
                ("2026-09-30", "2026-09-29", "2026-10-10"),
            )
            self.assertEqual(row["debit_lc"], 100 if row["journal_line"] == 0 else 0)
            self.assertEqual(row["credit_lc"], 100 if row["journal_line"] == 1 else 0)
        changed = next(
            r for r in rows if (r["journal_entry"], r["journal_line"]) == (2, 0)
        )
        self.assertEqual(
            (
                changed["line_posting_date"],
                changed["line_document_date"],
                changed["line_due_date"],
            ),
            ("2026-10-01", "2026-10-02", "2026-11-15"),
        )
        for row in rows:
            if row is not changed:
                self.assertEqual(row["line_posting_date"], row["posting_date"])
                self.assertEqual(row["line_document_date"], row["document_date"])
                self.assertEqual(row["line_due_date"], row["due_date"])
        october = [
            r for r in rows if "2026-10-01" <= r["line_posting_date"] < "2026-11-01"
        ]
        self.assertEqual(sum(r["net_debit_lc"] for r in october), 100)
        self.assertEqual(sum(r["net_debit_lc"] for r in rows), 0)


if __name__ == "__main__":
    unittest.main()
