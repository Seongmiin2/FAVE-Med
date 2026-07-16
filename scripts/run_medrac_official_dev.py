from __future__ import annotations

import argparse
import json
import os
import sys
import types
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a pinned official MedRaC development subset.")
    parser.add_argument("--items", type=int, choices=range(1, 11), default=3)
    parser.add_argument("--model", default="OpenAI/gpt-4o-mini")
    parser.add_argument("--output", type=Path, default=Path("reports/medrac_official_dev.json"))
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    official = project / "external" / "official" / "medrac"
    load_dotenv(project / ".env", override=False)
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not configured")
    sys.path.insert(0, str(official))
    os.chdir(official)
    # The official package imports local-model dependencies even for API-only
    # runs. A narrow shim keeps that unused path unavailable without editing the
    # pinned source checkout.
    transformers_shim = types.ModuleType("transformers")
    class _UnavailableLocalModel:
        @classmethod
        def from_pretrained(cls, *args, **kwargs):
            raise RuntimeError("Local transformer models are disabled in the API-only reproduction")
    transformers_shim.AutoTokenizer = _UnavailableLocalModel
    transformers_shim.AutoModelForCausalLM = _UnavailableLocalModel
    sys.modules["transformers"] = transformers_shim
    from evaluator import RegEvaluator
    from method.medRaC import MedRaC
    from model.gpt import APIModel

    model = APIModel(args.model, temperature=0.0, rpm_limit=100, tpm_limit=500_000)
    evaluator = RegEvaluator()
    method = MedRaC(llms=[model], evaluators=[evaluator], model=model, use_rag=True)
    method.row_numbers = list(range(args.items))
    raw_path = method.generate_raw(test=True, raw_json_dir="raw_output/fave_med_reproduction")
    eval_path = method.evaluate(raw_json_file=raw_path, eval_json_dir="eval_output/fave_med_reproduction")
    raw = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    evaluated = json.loads(Path(eval_path).read_text(encoding="utf-8"))
    input_tokens = sum(int(row.get("Input Tokens", 0) or 0) for row in raw)
    output_tokens = sum(int(row.get("Output Tokens", 0) or 0) for row in raw)
    correct = sum(row.get("Result") == "Correct" for row in evaluated)
    summary = {
        "status": "official_code_development_subset_completed",
        "repository": "https://github.com/Super-Billy/EMNLP-2025-MedRaC.git",
        "commit": "900c54123ce03ca467ebdf0b2f28afb7dcaabc5e",
        "model": args.model,
        "items": args.items,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "correct": correct,
        "accuracy": correct / args.items,
        "estimated_generation_cost_usd": input_tokens / 1_000_000 * 0.15 + output_tokens / 1_000_000 * 0.60,
        "pricing_note": "GPT-4o mini text-token list price checked 2026-07-16; embedding query cost excluded.",
        "evaluation_columns": sorted(set(evaluated[0]) - set(raw[0])) if evaluated else [],
        "environment_deviation": "Python 3.13 compatibility environment; dependency versions differ from official pins.",
        "raw_output": str((official / raw_path).resolve()),
        "evaluated_output": str((official / eval_path).resolve()),
    }
    destination = project / args.output
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
