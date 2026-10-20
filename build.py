#!/usr/bin/env python3
"""Build the portable MDL artifact from reviewed JSON sources; standard library only."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
COLUMN = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\Z")
LITERAL = re.compile(r"(?:-?\d+(?:\.\d+)?|'(?:[^']|'')*')\Z")
MODEL_KEYS = {"name", "displayName", "columns", "primaryKey", "uniqueKeys", "properties", "tableReference"}
COLUMN_KEYS = {"name", "displayName", "type", "notNull", "isHidden", "isCalculated", "properties"}
RELATIONSHIP_KEYS = {"name", "displayName", "models", "joinType", "condition", "properties"}
PROPERTY_KEYS = {"description", "sap_b1_source", "semanticUnitKind", "semanticUnitScope"}
DESCRIPTION = (
    "SAP Business One 标准表与关系模板，覆盖销售、采购、库存、生产和财务。"
    "按单据来源类型和复合键追溯，区分过账日期、凭证日期、创建日期及数量、币种和金额粒度。"
    "模板没有公司库连接、工作区信息或客户自定义指标；导入时须核验目标数据库的表、列和版本。"
    "库存成本、工单业务及历史余额仍需目标公司库和 SAP 标准报表验证。"
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    if metadata["entry"] != "mdl.json" or metadata["formatVersion"] != 1:
        raise ValueError("Unsupported template manifest")
    result = {
        "layoutVersion": metadata["layoutVersion"],
        "dataSource": metadata["dataSource"],
        "catalog": "sap_b1",
        "schema": metadata["defaultSchema"],
        "description": DESCRIPTION,
        "models": [],
        "relationships": [],
        "views": [],
        "cubes": [],
    }
    for directory, key in (("models", "models"), ("relationships", "relationships")):
        for path in sorted((root / directory).glob("*.json")):
            value = read_json(path)
            if path.stem != value["name"]:
                raise ValueError(f"Source filename must match object name: {path.name}")
            result[key].append(value)
        if not result[key]:
            raise ValueError(f"Empty template source directory: {directory}")
    validate(result, read_json(root / "validation" / "reference-contract.json"))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check that committed mdl.json is current")
    args = parser.parse_args()
    expected = encode(build())
    target = ROOT / "mdl.json"
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != expected:
            raise SystemExit("mdl.json differs from sources; run python3 build.py")
        print("mdl.json matches validated template sources")
    else:
        target.write_text(expected, encoding="utf-8")
        print("Built mdl.json")


if __name__ == "__main__":
    main()
