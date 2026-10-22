"""Exercise price interpretation and distribution-rule joins with normal business records."""

import sqlite3
import unittest
from contextlib import closing

from build import build


class MasterDataReviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mdl = build()
        cls.models = {m["name"]: m for m in cls.mdl["models"]}

    def relation(self, name):
        return next(
            r["condition"] for r in self.mdl["relationships"] if r["name"] == name
        )

    def test_price_currency_and_pricing_unit_remain_row_specific(self):
        with closing(sqlite3.connect(":memory:")) as db:
            for name in ("itm1", "ouom"):
                columns = ",".join(
                    f'"{c["name"]}" {c["type"]}' for c in self.models[name]["columns"]
                )
                db.execute(f'CREATE TABLE "{name}" ({columns})')
            db.executescript(
                "INSERT INTO ouom (UomEntry,UomCode,UomName) VALUES (1,'EA','Each'),(2,'KG','Kilogram');"
                "INSERT INTO itm1 (ItemCode,PriceList,Price,Currency,UomEntry,PriceType) VALUES "
                "('A',2,10,'USD',1,'I'),('B',2,10,'EUR',2,'P');"
            )
            rows = db.execute(
                "SELECT itm1.ItemCode,itm1.PriceList,itm1.Price,itm1.Currency,"
                "ouom.UomCode,itm1.PriceType FROM itm1 LEFT JOIN ouom ON "
                + self.relation("itm1_ouom")
                + " ORDER BY itm1.ItemCode"
            ).fetchall()
            self.assertEqual(
                rows, [("A", 2, 10, "USD", "EA", "I"), ("B", 2, 10, "EUR", "KG", "P")]
            )

    def test_rule_periods_and_weights_are_preserved_when_resolving_cost_centers(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.executescript(
                "CREATE TABLE ocr1 (OcrCode TEXT,PrcCode TEXT,ValidFrom TEXT,ValidTo TEXT,PrcAmount NUMERIC);"
                "CREATE TABLE oprc (PrcCode TEXT PRIMARY KEY,PrcName TEXT);"
                "INSERT INTO oprc VALUES ('C1','Assembly'),('C2','Packing');"
                "INSERT INTO ocr1 VALUES ('R','C1','2026-01-01','2026-06-30',60),"
                "('R','C2','2026-01-01','2026-06-30',40),"
                "('R','C1','2026-07-01',NULL,50),('R','C2','2026-07-01',NULL,50);"
            )
            rows = db.execute(
                "SELECT ocr1.ValidFrom,oprc.PrcName,ocr1.PrcAmount FROM ocr1 LEFT JOIN oprc ON "
                + self.relation("ocr1_oprc")
                + " ORDER BY ocr1.ValidFrom,ocr1.PrcCode"
            ).fetchall()
            self.assertEqual(len(rows), 4)
            self.assertEqual(
                [r[1] for r in rows], ["Assembly", "Packing", "Assembly", "Packing"]
            )
            self.assertEqual([r[2] for r in rows], [60, 40, 50, 50])


if __name__ == "__main__":
    unittest.main()
