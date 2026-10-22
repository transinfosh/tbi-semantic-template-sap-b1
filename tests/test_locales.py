"""English display metadata covers the default template without duplicating semantic structure."""

import hashlib
import json
import re
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAN = re.compile(r"[\u3400-\u9fff]")


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class TemplateLocalesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = read("template.json")
        cls.pack = read("locales/en.json")

    def check_entry(self, source, target, label):
        with self.subTest(entry=label):
            self.assertFalse(
                set(target)
                - {
                    "displayName",
                    "description",
                    "columns",
                    "dimensions",
                    "timeDimensions",
                    "measures",
                }
            )
            for key, original in (
                ("displayName", source.get("displayName")),
                (
                    "description",
                    source.get("description")
                    or source.get("properties", {}).get("description"),
                ),
            ):
                if original:
                    self.assertIn(key, target)
                    self.assertTrue(target[key].strip())
                    self.assertIsNone(HAN.search(target[key]), (label, key))
            if source.get("columns"):
                self.assertEqual(
                    set(target["columns"]),
                    {column["name"] for column in source["columns"]},
                )
                for column in source["columns"]:
                    self.check_entry(
                        column,
                        target["columns"][column["name"]],
                        label + "." + column["name"],
                    )

    def test_english_pack_is_declared_and_keeps_chinese_as_default(self):
        self.assertEqual(self.manifest["language"], "zh-CN")
        self.assertEqual(self.manifest["translations"]["en"], "locales/en.json")
        self.assertEqual(self.pack["formatVersion"], 1)
        self.assertFalse(
            set(self.pack)
            - {
                "formatVersion",
                "template",
                "groups",
                "models",
                "relationships",
                "views",
                "cubes",
            }
        )
        for key in ("title", "description"):
            self.assertTrue(self.pack["template"][key].strip())
            self.assertIsNone(HAN.search(self.pack["template"][key]))

    def test_all_objects_fields_and_groups_have_english_text(self):
        for kind in ("models", "relationships", "views", "cubes"):
            sources = [
                read(str(path.relative_to(ROOT)))
                for path in (ROOT / kind).glob("*.json")
            ]
            self.assertEqual(
                set(self.pack[kind]), {source["name"] for source in sources}
            )
            for source in sources:
                self.check_entry(
                    source, self.pack[kind][source["name"]], kind + "." + source["name"]
                )
        groups = read("groups.json")["groups"]
        self.assertEqual(set(self.pack["groups"]), {group["name"] for group in groups})
        for group in groups:
            translated = self.pack["groups"][group["name"]]
            self.assertEqual(set(translated), {"title"})
            self.assertTrue(translated["title"].strip())
            self.assertIsNone(HAN.search(translated["title"]))

    def test_representative_sap_terms_and_finance_distinctions_are_explicit(self):
        self.assertEqual(self.pack["models"]["oinv"]["displayName"], "A/R Invoice")
        self.assertEqual(self.pack["models"]["opch"]["displayName"], "A/P Invoice")
        self.assertEqual(
            self.pack["models"]["oitr"]["displayName"], "Internal Reconciliation"
        )
        fields = self.pack["models"]["jdt1"]["columns"]
        self.assertIn(
            "not a credit posted movement", fields["BalDueCred"]["description"]
        )
        self.assertIn("historical cutoff balance", fields["BalDueDeb"]["description"])
        self.assertIn("not FormatCode", fields["Account"]["description"])

    def test_descriptions_preserve_original_technical_identifiers(self):
        identifiers = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
        texts = {}
        for kind in ("models", "relationships", "views", "cubes"):
            for file in sorted((ROOT / kind).glob("*.json")):
                obj = read(str(file.relative_to(ROOT)))
                translated = self.pack[kind][obj["name"]]
                entries = [(obj["name"], obj, translated)] + [
                    (
                        obj["name"] + "." + field["name"],
                        field,
                        translated["columns"][field["name"]],
                    )
                    for field in obj.get("columns", [])
                ]
                for name, source, target in entries:
                    values = {
                        key: value
                        for key, value in (
                            ("displayName", source.get("displayName")),
                            (
                                "description",
                                source.get("description")
                                or source.get("properties", {}).get("description"),
                            ),
                        )
                        if value
                    }
                    texts[kind + "." + name] = values
                    lost = Counter(
                        identifiers.findall(values.get("description", ""))
                    ) - Counter(identifiers.findall(target.get("description", "")))
                    self.assertFalse(lost, (name, lost))
        texts["template"] = {
            key: self.manifest[key] for key in ("title", "description")
        }
        for group in read("groups.json")["groups"]:
            texts["groups." + group["name"]] = {"title": group["title"]}
        digest = hashlib.sha256(
            json.dumps(
                texts, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()
        self.assertEqual(
            digest,
            read("validation/en-source-text.json")["sourceTextSha256"],
            "Default wording changed; review and update the English language pack.",
        )


if __name__ == "__main__":
    unittest.main()
