import copy
import json
import tempfile
import unittest
from pathlib import Path

from build import ROOT, build, read_json, validate_groups


class TestTemplateGroups(unittest.TestCase):
    def setUp(self):
        self.mdl = build()
        self.metadata = read_json(ROOT / "template.json")
        self.groups = read_json(ROOT / "groups.json")
        self.sources = {
            **self.mdl,
            "models": [read_json(path) for path in sorted((ROOT / "models").glob("*.json"))],
        }

    def validate_fixture(self, value, path="groups.json", mdl=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "groups.json").write_text(json.dumps(value))
            validate_groups(root, {"groups": path}, self.sources if mdl is None else mdl)

    def test_seven_groups_cover_all_template_models_once(self):
        self.assertEqual(
            [group["title"] for group in self.groups["groups"]],
            ["主数据", "销售", "采购", "库存", "生产", "财务", "其他"],
        )
        self.assertTrue(all(set(group) == {"name", "title"} for group in self.groups["groups"]))
        codes = {group["name"] for group in self.groups["groups"]}
        names = [model["name"] for model in self.sources["models"] if model["group"] in codes]
        self.assertEqual(len(names), 101)
        self.assertEqual(set(names), {model["name"] for model in self.mdl["models"]})
        self.assertEqual(len(names), len(set(names)))
        self.assertNotIn("groups", self.mdl)
        self.assertNotIn("_template_groups", self.mdl)
        self.assertTrue(all("group" not in model for model in self.mdl["models"]))

    def test_master_data_and_business_transactions_have_explicit_ownership(self):
        membership = {model["name"]: model["group"] for model in self.sources["models"]}
        for name in ("oact", "oprc", "oprj", "owhs", "obin", "orsc", "oitm", "ocrd"):
            self.assertEqual(membership[name], "master_data")
        for name in ("oadm", "nnm1", "ortt"):
            self.assertEqual(membership[name], "other")
        self.assertEqual(membership["oitt"], "production")
        self.assertEqual(membership["ige1"], "inventory")
        self.assertEqual(membership["jdt1"], "finance")

    def test_unknown_and_duplicate_membership_are_rejected(self):
        for kind in ("unknown", "inside", "between"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                value = copy.deepcopy(self.groups)
                name = "oitm"
                value["groups"][0]["models"] = []
                if kind == "unknown":
                    value["groups"][0]["models"].append("unknown_model")
                elif kind == "inside":
                    value["groups"][0]["models"].extend([name, name])
                else:
                    value["groups"][1]["models"] = [name]
                self.validate_fixture(value)

    def test_duplicate_normalized_titles_and_codes_are_rejected(self):
        for key in ("name", "title"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                value = copy.deepcopy(self.groups)
                value["groups"][1][key] = value["groups"][0][key]
                if key == "name":
                    value["groups"][1][key] = value["groups"][1][key].upper()
                self.validate_fixture(value)

    def test_legacy_templates_can_omit_group_file(self):
        validate_groups(ROOT, {}, self.mdl)

    def test_paths_versions_and_instance_metadata_are_rejected(self):
        for path in ("../groups.json", "/tmp/groups.json", "groups.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.validate_fixture(self.groups, path)
        value = copy.deepcopy(self.groups)
        value["formatVersion"] = True
        with self.assertRaises(ValueError):
            self.validate_fixture(value)
        value = copy.deepcopy(self.groups)
        value["groups"][0]["workspace"] = "private_workspace"
        with self.assertRaises(ValueError):
            self.validate_fixture(value)

    def test_model_group_must_reference_a_declared_group(self):
        for code in ("unknown", False, ["sales"]):
            with self.subTest(code=code), self.assertRaises(ValueError):
                source = copy.deepcopy(self.sources)
                source["models"][0]["group"] = code
                self.validate_fixture(self.groups, mdl=source)
        with self.assertRaises(ValueError):
            validate_groups(ROOT, {}, self.sources)

    def test_matching_legacy_membership_can_be_read_without_duplicating_current_source(self):
        value = copy.deepcopy(self.groups)
        for group in value["groups"]:
            group["models"] = [
                model["name"] for model in self.sources["models"] if model["group"] == group["name"]
            ]
        self.validate_fixture(value)
