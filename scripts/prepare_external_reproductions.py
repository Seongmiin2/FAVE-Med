from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SOURCES = {
    "crag": ("https://github.com/HuskyInSalt/CRAG.git", "de7c2961ae624a1483a138c5798e1f6d0c4fb0e0"),
    "medrac": ("https://github.com/Super-Billy/EMNLP-2025-MedRaC.git", "900c54123ce03ca467ebdf0b2f28afb7dcaabc5e"),
}


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch pinned official external-method sources without modifying them.")
    parser.add_argument("--root", default="external/official")
    args = parser.parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    for name, (url, commit) in SOURCES.items():
        target = root / name
        if not target.exists():
            run(["git", "clone", "--filter=blob:none", url, str(target)])
        run(["git", "-C", str(target), "fetch", "origin", commit])
        run(["git", "-C", str(target), "checkout", "--detach", commit])
        actual = subprocess.check_output(["git", "-C", str(target), "rev-parse", "HEAD"], text=True).strip()
        if actual != commit:
            raise RuntimeError(f"{name}: expected {commit}, got {actual}")
        print(f"{name}: {actual}")


if __name__ == "__main__":
    main()
