from __future__ import annotations

from pathlib import Path

from ..core.jsonl_utils import read_jsonl


def load_corpus(path: str | Path) -> list[dict]:
    rows = list(read_jsonl(path))
    required = {"evidence_id", "text", "source_id", "source_type"}
    for index, row in enumerate(rows, 1):
        missing = required - row.keys()
        if missing:
            raise ValueError(f"Corpus row {index} missing fields: {sorted(missing)}")
    return rows
