from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

REVISION = "591157b3343b4dda247294f9d929da4c75026fa8"
URL = f"https://huggingface.co/datasets/nsk7153/MedCalc-Bench-Verified/resolve/{REVISION}/test_data.csv"
OUTPUT = Path("data/medical/raw/medcalc_bench_verified/test_data.csv")


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(URL, timeout=120) as response, OUTPUT.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {"repository": "nsk7153/MedCalc-Bench-Verified", "revision": REVISION, "file": "test_data.csv", "sha256": digest, "bytes": OUTPUT.stat().st_size, "license": "CC-BY-SA-4.0"}
    OUTPUT.with_name("manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
