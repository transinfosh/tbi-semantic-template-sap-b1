"""Business identity checks using the actual portable relationships and synthetic data."""

import sqlite3
import sys
import unittest
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build import build


class CrossModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mdl = build()
        cls.models = {m['name']: m for m in mdl['models']}
        cls.relationships = mdl['relationships']

    def relation(self, first, second):
        matches = [r for r in self.relationships if set(r['models']) == {first, second}]
        self.assertEqual(len(matches), 1)
        return matches[0]['condition']

    def test_purchasing_sources_keep_document_type_and_original_line(self):
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript(
                'CREATE TABLE por1 (DocEntry INT, LineNum INT, Quantity NUMERIC);'
                'CREATE TABLE pdn1 (DocEntry INT, LineNum INT, BaseEntry INT, BaseLine INT, '
                'BaseType INT, Quantity NUMERIC);'
                'CREATE TABLE pch1 (DocEntry INT, LineNum INT, BaseEntry INT, BaseLine INT, '
                'BaseType INT, Quantity NUMERIC);'
                'INSERT INTO por1 VALUES (11, 0, 10), (11, 2, 50);'
                'INSERT INTO pdn1 VALUES (21, 4, 11, 0, 22, 3), (22, 8, 11, 0, 22, 2), '
                '(23, 4, 11, 0, 18, 90);'
                'INSERT INTO pch1 VALUES (31, 9, 21, 4, 20, 1), (32, 7, 21, 4, 22, 90);'
            )
            received = db.execute(
                'SELECT SUM(pdn1.Quantity) FROM por1 JOIN pdn1 ON '
                + self.relation('pdn1', 'por1')
            ).fetchone()[0]
            invoiced = db.execute(
                'SELECT SUM(pch1.Quantity) FROM pdn1 JOIN pch1 ON '
                + self.relation('pch1', 'pdn1')
            ).fetchone()[0]
            self.assertEqual((received, invoiced), (5, 1))

    def test_bom_resources_use_type_and_internal_code_without_item_collisions(self):
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript(
                'CREATE TABLE itt1 (Father TEXT, ChildNum INT, Code TEXT, Type INT);'
                'CREATE TABLE oitm (ItemCode TEXT, ItemName TEXT);'
                'CREATE TABLE orsc (ResCode TEXT, VisResCode TEXT, ResName TEXT);'
                "INSERT INTO itt1 VALUES ('F', 0, 'X', 4), ('F', 1, 'X', 290), "
                "('F', 2, 'X', -18), ('F', 3, 'X', -99);"
                "INSERT INTO oitm VALUES ('X', 'Material');"
                "INSERT INTO orsc VALUES ('X', 'DISPLAY-X', 'Resource');"
            )
            rows = db.execute(
                'SELECT itt1.ChildNum, oitm.ItemName, orsc.ResName FROM itt1 '
                'LEFT JOIN oitm ON ' + self.relation('itt1', 'oitm')
                + ' LEFT JOIN orsc ON ' + self.relation('itt1', 'orsc')
                + ' ORDER BY itt1.ChildNum'
            ).fetchall()
            self.assertEqual(rows, [(0, 'Material', None), (1, None, 'Resource'),
                                    (2, None, None), (3, None, None)])

    def test_serial_balance_keeps_item_warehouse_and_master_id_distinct(self):
        model = self.models['osrq']
        unique = model['uniqueKeys'][0]
        with closing(sqlite3.connect(':memory:')) as db:
            db.executescript(
                'CREATE TABLE osrn (AbsEntry INT PRIMARY KEY, ItemCode TEXT, '
                'SysNumber INT, DistNumber TEXT);'
                'CREATE TABLE osrq (AbsEntry INT PRIMARY KEY, ItemCode TEXT, SysNumber INT, '
                'WhsCode TEXT, MdAbsEntry INT, Quantity NUMERIC, UNIQUE ('
                + ','.join(unique) + '));'
                "INSERT INTO osrn VALUES (101, 'A', 7, 'SERIAL-A'), (202, 'B', 7, 'SERIAL-B');"
                "INSERT INTO osrq VALUES (1, 'A', 7, 'W1', 101, 1), "
                "(2, 'A', 7, 'W2', 101, 0), (3, 'B', 7, 'W1', 202, 1);"
            )
            rows = db.execute(
                'SELECT osrq.ItemCode, osrq.WhsCode, osrn.DistNumber, osrq.Quantity '
                'FROM osrq LEFT JOIN osrn ON ' + self.relation('osrq', 'osrn')
                + ' ORDER BY osrq.AbsEntry'
            ).fetchall()
            self.assertEqual(rows, [('A', 'W1', 'SERIAL-A', 1), ('A', 'W2', 'SERIAL-A', 0),
                                    ('B', 'W1', 'SERIAL-B', 1)])
            with self.assertRaises(sqlite3.IntegrityError):
                db.execute("INSERT INTO osrq VALUES (4, 'A', 7, 'W1', 101, 1)")


if __name__ == '__main__':
    unittest.main()
