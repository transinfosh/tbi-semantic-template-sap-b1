#!/usr/bin/env python3
"""Validate portable template sources and optionally export MDL; standard library only."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
COLUMN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\Z")
LITERAL = re.compile(r"(?:-?\d+(?:\.\d+)?|'(?:[^']|'')*')\Z")
MODEL_KEYS = {"name", "displayName", "columns", "primaryKey", "uniqueKeys", "properties", "tableReference"}
COLUMN_KEYS = {"name", "displayName", "type", "notNull", "isHidden", "isCalculated", "properties"}
RELATIONSHIP_KEYS = {"name", "displayName", "models", "joinType", "condition", "properties"}
PROPERTY_KEYS = {"description", "sap_b1_source", "semanticUnitKind", "semanticUnitScope"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_groups(root: Path, metadata: dict, mdl: dict) -> None:
    """Validate optional classification data without adding it to the exported MDL."""
    if "groups" not in metadata:
        return
    relative = metadata["groups"]
    if (
        not isinstance(relative, str)
        or not relative
        or PurePosixPath(relative).is_absolute()
        or "\\" in relative
        or any(part in ("", ".", "..") for part in relative.split("/"))
        or PurePosixPath(relative).suffix != ".json"
    ):
        raise ValueError("Invalid group file path")
    path = root / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Group file must be a regular JSON file inside the repository")
    value = read_json(path)
    if (
        not isinstance(value, dict)
        or set(value) != {"formatVersion", "groups"}
        or type(value.get("formatVersion")) is not int
        or value["formatVersion"] != 1
        or not isinstance(value.get("groups"), list)
        or len(value["groups"]) > 2000
    ):
        raise ValueError("Groups require formatVersion 1 and a groups array")
    kinds = ("models", "views", "cubes")
    known = {kind: {item["name"] for item in mdl.get(kind, [])} for kind in kinds}
    used = {kind: set() for kind in kinds}
    names, titles = set(), set()
    for group in value["groups"]:
        if not isinstance(group, dict) or set(group) - {"name", "title", *kinds}:
            raise ValueError("Unsupported group fields")
        name, title = group.get("name"), group.get("title")
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
            raise ValueError("Invalid portable group code")
        if not isinstance(title, str) or any(
            unicodedata.category(char) in {"Cc", "Cf", "Cs", "Zl", "Zp"} for char in title
        ):
            raise ValueError("Invalid group title")
        title = unicodedata.normalize("NFC", title).strip()
        if not title or len(title) > 140 or name.casefold() in names or title in titles:
            raise ValueError("Empty or duplicate group code/title")
        names.add(name.casefold())
        titles.add(title)
        for kind in kinds:
            members = group.get(kind, [])
            if (
                not isinstance(members, list)
                or any(not isinstance(member, str) or member not in known[kind] for member in members)
                or len(members) != len(set(members))
                or used[kind].intersection(members)
            ):
                raise ValueError("Unknown or duplicate group membership")
            used[kind].update(members)


def encode(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _names(values: list[dict], label: str) -> dict[str, dict]:
    result = {}
    for value in values:
        name = value["name"]
        if not IDENTIFIER.fullmatch(name) or name.lower() in result:
            raise ValueError(f"Invalid or duplicate {label}: {name}")
        result[name.lower()] = value
    return result


def _properties(value: dict, label: str) -> None:
    if set(value) - PROPERTY_KEYS:
        raise ValueError(f"Instance or unsupported properties in {label}")


def condition_columns(condition: str) -> list[tuple[str, str]]:
    """The template deliberately supports only AND-connected equality predicates."""
    columns = []
    for predicate in re.split(r"\s+AND\s+", condition, flags=re.IGNORECASE):
        parts = predicate.strip().split("=")
        if len(parts) != 2:
            raise ValueError(f"Unsupported relationship predicate: {predicate}")
        references = 0
        for part in parts:
            operand = part.strip()
            match = COLUMN.fullmatch(operand)
            if match:
                columns.append((match[1], match[2]))
                references += 1
            elif not LITERAL.fullmatch(operand):
                raise ValueError(f"Unsupported relationship operand: {operand}")
        if not references:
            raise ValueError(f"Relationship predicate has no column: {predicate}")
    return columns


def validate(mdl: dict, reference: dict) -> None:
    if mdl["layoutVersion"] != 4 or mdl["dataSource"] != "MSSQL":
        raise ValueError("This template requires MSSQL and MDL layoutVersion 4")
    if mdl.get("views") or mdl.get("cubes"):
        raise ValueError("Customer-specific Views and Cubes must stay in the workspace")
    models = _names(mdl["models"], "model")
    columns = {}
    for model in models.values():
        name = model["name"]
        if set(model) - MODEL_KEYS:
            raise ValueError(f"Instance or unsupported model fields: {name}")
        table = model["tableReference"]
        if set(table) != {"schema", "table"} or table["schema"] != "dbo":
            raise ValueError(f"Physical company catalog or nondefault schema in {name}")
        if not IDENTIFIER.fullmatch(table["table"]) or table["table"] not in reference:
            raise ValueError(f"Nonstandard or undocumented table: {name}")
        _properties(model.get("properties", {}), name)
        fields = _names(model["columns"], f"column in {name}")
        columns[name] = {column["name"] for column in fields.values()}
        documented = reference[table["table"]]
        for column in fields.values():
            field = column["name"]
            if field.upper().startswith("U_") or column.get("isCalculated"):
                raise ValueError(f"Customer or calculated field in {name}.{field}")
            if set(column) - COLUMN_KEYS or field not in documented["columns"]:
                raise ValueError(f"Unsupported or undocumented column in {name}.{field}")
            _properties(column.get("properties", {}), f"{name}.{field}")
        primary = model["primaryKey"]
        primary = [primary] if isinstance(primary, str) else primary
        if primary != documented["primary_key"]:
            raise ValueError(f"Primary key differs from official reference in {name}")
        for key in [primary, *model.get("uniqueKeys", [])]:
            if not key or not set(key) <= columns[name]:
                raise ValueError(f"Missing key columns in {name}")

    for relation in _names(mdl["relationships"], "relationship").values():
        name = relation["name"]
        if set(relation) - RELATIONSHIP_KEYS:
            raise ValueError(f"Instance or unsupported relationship fields: {name}")
        _properties(relation.get("properties", {}), name)
        endpoints = relation["models"]
        if len(endpoints) != 2 or len(set(endpoints)) != 2 or not set(endpoints) <= models.keys():
            raise ValueError(f"Invalid relationship endpoints: {name}")
        if relation["joinType"] not in {"ONE_TO_ONE", "ONE_TO_MANY", "MANY_TO_ONE", "MANY_TO_MANY"}:
            raise ValueError(f"Invalid relationship cardinality: {name}")
        references = condition_columns(relation["condition"])
        if {table for table, _ in references} != set(endpoints):
            raise ValueError(f"Relationship must reference exactly its two models: {name}")
        for table, field in references:
            if field not in columns[table]:
                raise ValueError(f"Missing relationship column {table}.{field} in {name}")


def build(root: Path = ROOT) -> dict:
    metadata = read_json(root / "template.json")
    if metadata.get("formatVersion") != 1 or "entry" in metadata:
        raise ValueError("Unsupported template manifest")
    sources = metadata.get("sources")
    if not isinstance(sources, dict) or set(sources) != {"models", "relationships"}:
        raise ValueError("Template sources must declare model and relationship directories")
    for field in ("catalog", "description", "defaultSchema"):
        if not isinstance(metadata.get(field), str) or not metadata[field].strip():
            raise ValueError(f"Template {field} must be a nonempty string")
    result = {
        "layoutVersion": metadata["layoutVersion"],
        "dataSource": metadata["dataSource"],
        "catalog": metadata["catalog"],
        "schema": metadata["defaultSchema"],
        "description": metadata["description"],
        "models": [],
        "relationships": [],
        "views": [],
        "cubes": [],
    }
    for key in ("models", "relationships"):
        relative = sources[key]
        if (
            not isinstance(relative, str)
            or not relative
            or PurePosixPath(relative).is_absolute()
            or "\\" in relative
            or any(part in ("", ".", "..") for part in relative.split("/"))
        ):
            raise ValueError(f"Invalid template source directory: {key}")
        directory = root / relative
        if (
            not directory.is_dir()
            or directory.is_symlink()
            or not directory.resolve().is_relative_to(root.resolve())
        ):
            raise ValueError(f"Source directory must stay inside the repository: {key}")
        for path in sorted(directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Source must be a regular JSON file: {path.name}")
            value = read_json(path)
            if path.stem != value["name"]:
                raise ValueError(f"Source filename must match object name: {path.name}")
            result[key].append(value)
        if not result[key]:
            raise ValueError(f"Empty template source directory: {relative}")
    validate(result, read_json(root / "validation" / "reference-contract.json"))
    validate_groups(root, metadata, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument(
        "--check", action="store_true", help="Validate manifest and split sources without writing"
    )
    options.add_argument(
        "--output", type=Path, help="Explicitly export assembled MDL to this optional local file"
    )
    args = parser.parse_args()
    mdl = build()
    if args.output:
        args.output.write_text(encode(mdl), encoding="utf-8")
        print(f"Exported validated MDL to {args.output}")
    else:
        print(
            f"Validated {len(mdl['models'])} models and {len(mdl['relationships'])} relationships; no file written"
        )


if __name__ == "__main__":
    main()
