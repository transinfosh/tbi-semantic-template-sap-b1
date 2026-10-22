"""Read the reviewed workspace extension without writing a site or a source database."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_pack() -> dict:
    pack = json.loads((ROOT / "pack.json").read_text(encoding="utf-8"))
    for view in pack["views"]:
        path = (ROOT / view["statementFile"]).resolve()
        if not path.is_relative_to(ROOT) or path.suffix != ".sql":
            raise ValueError("View statements must be SQL files inside the extension")
        view["statement"] = path.read_text(encoding="utf-8")
    return pack
