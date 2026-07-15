from __future__ import annotations

from pathlib import Path

import yaml


def load_config(path: str) -> tuple[dict, Path]:
    config_path = Path(path).resolve()
    with config_path.open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    root = config_path.parents[2]
    return config, root


def load_items(config: dict, root: Path):
    path = str(root / config["input_path"])
    if config["domain"] == "telecom":
        from ..domains.telecom.adapter import load_telecom_items

        return load_telecom_items(path)
    from ..domains.medical.adapter import load_medical_items

    return load_medical_items(path)
