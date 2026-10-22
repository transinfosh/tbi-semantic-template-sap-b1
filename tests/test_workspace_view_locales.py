"""Extension language overlays preserve executable semantics and business identifiers."""

import hashlib
import importlib.util
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "validation" / "workspace-views"
spec = importlib.util.spec_from_file_location(
    "localized_extension", ROOT / "load_pack.py"
)
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
IDENTIFIERS = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
HAN = re.compile(r"[\u3400-\u9fff]")


def display_sources(pack):
    result = {}
    for kind in ("models", "relationships", "views"):
        for item in pack[kind]:
            name = kind + "." + item["name"]
            result[name] = {
                "displayName": item.get("displayName") or item.get("title"),
                "description": item.get("description")
                or item.get("properties", {}).get("description", ""),
            }
            if kind == "views":
                for field, title in item["columnTitles"].items():
                    result[name + "." + field] = {"displayName": title}
            elif kind == "models":
                for col in item["columns"]:
                    result[name + "." + col["name"]] = {
                        "displayName": col["displayName"],
                        "description": col.get("properties", {}).get("description", ""),
                    }
    return result


def executable(value):
    if isinstance(value, list):
        return [executable(item) for item in value]
    if isinstance(value, dict):
        return {
            key: executable(item)
            for key, item in value.items()
            if key not in {"displayName", "title", "description", "columnTitles"}
        }
    return value


class WorkspaceViewLocalesTest(unittest.TestCase):
    def test_complete_english_coverage_including_all_view_fields(self):
        source = loader.load_pack()
        translated = loader.load_pack("en")
        overlay = json.loads((ROOT / "locales" / "en.json").read_text())
        self.assertEqual(
            (
                len(translated["models"]),
                len(translated["relationships"]),
                len(translated["views"]),
            ),
            (4, 14, 16),
        )
        self.assertEqual(sum(len(v["columnTitles"]) for v in translated["views"]), 325)
        for kind in ("models", "relationships", "views"):
            self.assertEqual(
                set(overlay[kind]), {item["name"] for item in source[kind]}
            )
            for item in source[kind]:
                if kind in {"models", "views"}:
                    fields = (
                        set(item["columnTitles"])
                        if kind == "views"
                        else {c["name"] for c in item["columns"]}
                    )
                    self.assertEqual(
                        set(overlay[kind][item["name"]]["columns"]), fields
                    )
        for name, entry in display_sources(translated).items():
            for key, text in entry.items():
                with self.subTest(name=name, field=key):
                    self.assertIsNone(HAN.search(text))
                    if display_sources(source)[name].get(key):
                        self.assertTrue(text.strip())

    def test_language_fallback_keeps_default_chinese_and_regional_english(self):
        source = loader.load_pack()
        for language in (None, "", "zh", "zh-CN", "zh-TW", "fr-FR"):
            with self.subTest(language=language):
                self.assertEqual(loader.load_pack(language), source)
        english = loader.load_pack("en")
        for language in ("en-US", "en_GB", "EN"):
            self.assertEqual(loader.load_pack(language), english)
        self.assertEqual(loader.load_pack(), source)
        self.assertEqual(source["views"][0]["title"], "销售订单到收款追溯")

    def test_translation_preserves_sql_keys_types_order_and_identifier_meaning(self):
        source = loader.load_pack()
        english = loader.load_pack("en")
        self.assertEqual(executable(source), executable(english))
        for first, second in zip(source["views"], english["views"]):
            self.assertEqual(list(first["columnTitles"]), list(second["columnTitles"]))
            self.assertEqual(first["statement"], second["statement"])
        original = display_sources(source)
        for name, entry in display_sources(english).items():
            missing = Counter(
                IDENTIFIERS.findall(original[name].get("description", ""))
            ) - Counter(IDENTIFIERS.findall(entry.get("description", "")))
            self.assertFalse(missing, (name, missing))
        self.assertIn(
            "without filling one from the other", english["views"][-1]["description"]
        )
        trace = next(
            v for v in english["views"] if v["name"] == "sales_order_to_cash_trace"
        )
        self.assertIn("Path counts are not document counts", trace["description"])

    def test_only_display_text_can_be_overridden(self):
        name = "sales_order_to_cash_trace"
        for overlay in (
            {"statement": "SELECT 1"},
            {"columns": {"unknown_field": {"displayName": "Unknown"}}},
            {"columns": {"order_entry": {"type": "VARCHAR"}}},
        ):
            with self.subTest(overlay=overlay), self.assertRaises(ValueError):
                loader._localize(
                    loader.load_pack(), {"formatVersion": 1, "views": {name: overlay}}
                )
        with self.assertRaises(ValueError):
            loader._read_resource("../reference-contract.json", ".json")
        with self.assertRaises(ValueError):
            loader.load_pack(False)

    def test_source_wording_fingerprint_requires_translation_review(self):
        source = display_sources(loader.load_pack())
        digest = hashlib.sha256(
            json.dumps(
                source, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        expected = json.loads((ROOT / "locales" / "source-text.json").read_text())
        self.assertEqual(digest, expected["sourceTextSha256"])


if __name__ == "__main__":
    unittest.main()
