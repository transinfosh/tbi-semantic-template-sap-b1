"""Read the reviewed workspace extension without writing a site or a source database."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _read_resource(relative: str, suffix: str) -> str:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or path.suffix != suffix:
        raise ValueError("Extension resources must stay inside the extension directory")
    return path.read_text(encoding="utf-8")


def _display_text(item: dict, translation: dict, *, view: bool = False) -> None:
    fields = {"displayName", "description"}
    if set(translation) - fields:
        raise ValueError("Translations can only change display text")
    for key, value in translation.items():
        if not isinstance(value, str):
            raise TypeError("Translated display text must be a string")
        if not value.strip():
            continue
        if key == "description" and "description" not in item and "properties" in item:
            item["properties"][key] = value
        else:
            item["title" if view and key == "displayName" else key] = value


def _localize(pack: dict, translation: dict) -> None:
    kinds = ("models", "relationships", "views")
    if (
        type(translation.get("formatVersion")) is not int
        or translation["formatVersion"] != 1
    ):
        raise ValueError("Extension translations require formatVersion 1")
    if set(translation) - {"formatVersion", *kinds}:
        raise ValueError("Unsupported extension translation sections")
    for kind in kinds:
        objects = {item["name"]: item for item in pack[kind]}
        entries = translation.get(kind, {})
        if not isinstance(entries, dict) or set(entries) - objects.keys():
            raise ValueError("Translations reference unknown extension objects")
        for name, overlay in entries.items():
            item = objects[name]
            if not isinstance(overlay, dict) or set(overlay) - {
                "displayName",
                "description",
                "columns",
            }:
                raise ValueError("Unsupported translated object fields")
            _display_text(
                item,
                {k: v for k, v in overlay.items() if k != "columns"},
                view=kind == "views",
            )
            if "columns" not in overlay:
                continue
            columns = (
                {
                    name: {"displayName": title}
                    for name, title in item["columnTitles"].items()
                }
                if kind == "views"
                else {col["name"]: col for col in item.get("columns", [])}
            )
            translated_columns = overlay["columns"]
            if (
                not isinstance(translated_columns, dict)
                or set(translated_columns) - columns.keys()
            ):
                raise ValueError("Translations reference unknown extension fields")
            for field, text in translated_columns.items():
                if not isinstance(text, dict):
                    raise TypeError("Translated field metadata must be an object")
                if kind == "views" and set(text) - {"displayName"}:
                    raise ValueError(
                        "View field translations only provide display names"
                    )
                _display_text(columns[field], text)
                if kind == "views":
                    item["columnTitles"][field] = columns[field]["displayName"]


def load_pack(language: str | None = None) -> dict:
    """Load source text by default, with region/base fallback for optional translations."""
    pack = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
    for view in pack["views"]:
        view["statement"] = _read_resource(view["statementFile"], ".sql")
    if language in (None, ""):
        language = pack.get("language", "zh-CN")
    if not isinstance(language, str) or not re.fullmatch(
        r"[A-Za-z]{2,3}(?:[-_][A-Za-z0-9]{2,8})*", language
    ):
        raise ValueError("Invalid extension language")
    requested = language.replace("_", "-").lower()
    default = pack.get("language", "zh-CN").replace("_", "-").lower()
    if requested not in {default, default.split("-")[0]}:
        paths = {
            code.replace("_", "-").lower(): path
            for code, path in pack.get("translations", {}).items()
        }
        relative = paths.get(requested) or paths.get(requested.split("-")[0])
        if relative:
            _localize(pack, json.loads(_read_resource(relative, ".json")))
    return pack
