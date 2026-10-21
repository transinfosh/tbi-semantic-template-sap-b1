"""Portable template invariants and representative join behavior, without Frappe or network."""

from __future__ import annotations

import copy
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from build import build, encode, read_json, validate


class TemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mdl = build()
        cls.reference = read_json(ROOT / "validation" / "reference-contract.json")

    def source_copy(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        target = Path(temporary.name)
        paths = [
            ROOT / "template.json",
            ROOT / "groups.json",
            ROOT / "build.py",
            ROOT / "validation" / "reference-contract.json",
        ]
        for directory in ("models", "relationships", "views", "cubes"):
            (target / directory).mkdir(parents=True, exist_ok=True)
            paths.extend((ROOT / directory).glob("*.json"))
            placeholder = ROOT / directory / ".gitkeep"
            if placeholder.exists():
                paths.append(placeholder)
        for source in sorted(paths, reverse=True):
            destination = target / source.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        return target

    def test_split_sources_assemble_deterministically_without_a_committed_artifact(self) -> None:
        source = self.source_copy()
        self.assertFalse((source / "mdl.json").exists())
        self.assertEqual(encode(build(source)), encode(self.mdl))
        metadata = read_json(source / "template.json")
        self.assertEqual(self.mdl["catalog"], metadata["catalog"])
        self.assertEqual(self.mdl["description"], metadata["description"])

    def test_default_and_check_commands_do_not_write_an_artifact(self) -> None:
        source = self.source_copy()
        before = {path.relative_to(source) for path in source.rglob("*")}
        for arguments in ([], ["--check"]):
            with self.subTest(arguments=arguments):
                subprocess.run(
                    [sys.executable, str(source / "build.py"), *arguments], check=True, capture_output=True
                )
                self.assertEqual({path.relative_to(source) for path in source.rglob("*")}, before)

    def test_reserved_directories_survive_git_and_do_not_change_the_assembled_mdl(self) -> None:
        source = self.source_copy()
        subprocess.run(["git", "init", "--quiet", str(source)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(source), "add", "."], check=True, capture_output=True)
        tracked = subprocess.run(
            ["git", "-C", str(source), "ls-files"], check=True, capture_output=True, text=True
        ).stdout.splitlines()
        for kind in ("views", "cubes"):
            self.assertIn(f"{kind}/.gitkeep", tracked)
        expected = encode(build(source))
        manifest = read_json(source / "template.json")
        for kind in ("views", "cubes"):
            manifest["sources"].pop(kind)
            shutil.rmtree(source / kind)
        (source / "template.json").write_text(encode(manifest), encoding="utf-8")
        self.assertEqual(encode(build(source)), expected)

    def test_reserved_directories_cannot_silently_import_unreviewed_definitions(self) -> None:
        source = self.source_copy()
        for kind in ("views", "cubes"):
            with self.subTest(kind=kind):
                path = source / kind / "unreviewed.json"
                path.write_text(encode({"name": "unreviewed"}), encoding="utf-8")
                try:
                    with self.assertRaisesRegex(ValueError, "Views and Cubes must stay in the workspace"):
                        build(source)
                finally:
                    path.unlink()

    def test_explicit_export_matches_the_assembled_sources(self) -> None:
        source = self.source_copy()
        output = source / "optional-export.json"
        subprocess.run(
            [sys.executable, str(source / "build.py"), "--output", str(output)],
            check=True,
            capture_output=True,
        )
        self.assertEqual(output.read_text(encoding="utf-8"), encode(self.mdl))
        self.assertFalse((source / "mdl.json").exists())

    def test_manifest_directory_cannot_escape_the_repository(self) -> None:
        source = self.source_copy()
        manifest = read_json(source / "template.json")
        for directory in ("../models", "/tmp/models", "models/../models", "models\\child"):
            with self.subTest(directory=directory):
                manifest["sources"]["models"] = directory
                (source / "template.json").write_text(encode(manifest), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "Invalid template source directory"):
                    build(source)

    def test_manifest_does_not_accept_the_old_generated_file_entry(self) -> None:
        source = self.source_copy()
        manifest = read_json(source / "template.json")
        manifest["entry"] = "mdl.json"
        (source / "template.json").write_text(encode(manifest), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Unsupported template manifest"):
            build(source)

    def test_symlink_source_is_rejected(self) -> None:
        source = self.source_copy()
        path = source / "models" / "oitm.json"
        path.unlink()
        path.symlink_to(ROOT / "models" / "oitm.json")
        with self.assertRaisesRegex(ValueError, "regular JSON file"):
            build(source)

    def test_artifact_has_no_customer_connection_or_instance_policy(self) -> None:
        text = json.dumps(self.mdl, ensure_ascii=False)
        self.assertNotRegex(text, r"(?i)/home/|password|row_security|connection_id|enrollment_id")
        self.assertNotRegex(text, r"https?://(?!help\.sap\.com/)")
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
            self.assertNotIn(set(relation["models"]), [{"oivl", "ign1"}, {"oivl", "wtr1"}])

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
        with closing(sqlite3.connect(":memory:")) as connection:
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
        with closing(sqlite3.connect(":memory:")) as connection:
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
