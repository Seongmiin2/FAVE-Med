from __future__ import annotations

import argparse
import random

from dotenv import load_dotenv

from ..core.jsonl_utils import read_jsonl, write_jsonl
from ..pipelines import run_pipeline
from ..providers.mock_provider import MockProvider
from .common import load_config, load_items


def make_provider(config):
    model = config["model"]
    if model.get("provider") == "mock":
        return MockProvider()
    from ..providers.openai_provider import OpenAIProvider

    return OpenAIProvider(model["name"], model.get("temperature", 0), model.get("max_retries", 3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--method", choices=["llm_only", "cot", "vanilla_rag", "fave", "fave_silent", "demo", "demo_multi_executor", "fave_demo", "demo_oracle_executor", "fave_oracle_executor", "demo_predicted_executor", "fave_predicted_executor", "vanilla_controlled_rag", "fave_controlled", "vanilla_retrieval_rag", "fave_retrieval", "vanilla_retrieval_predicted_executor", "fave_retrieval_predicted_executor"])
    parser.add_argument("--max-items", type=int, help="run only the first N benchmark items")
    args = parser.parse_args()
    load_dotenv()
    config, root = load_config(args.config)
    random.seed(config.get("runtime", {}).get("seed", 42))
    items, provider = load_items(config, root), make_provider(config)
    if args.max_items is not None:
        if args.max_items < 1:
            parser.error("--max-items must be at least 1")
        items = items[: args.max_items]
    methods = [args.method] if args.method else config["methods"]
    runtime_by_id = {}
    if config["domain"] == "telecom":
        from ..domains.telecom.adapter import load_telecom_records

        runtime_by_id = {record.runtime.id: record.runtime for record in load_telecom_records(str(root / config["input_path"]))}
    predicted_methods = {"demo_predicted_executor", "fave_predicted_executor", "vanilla_controlled_rag", "fave_controlled", "vanilla_retrieval_rag", "fave_retrieval", "vanilla_retrieval_predicted_executor", "fave_retrieval_predicted_executor"}
    for method in methods:
        output = root / config["output_dir"] / f"{method}.jsonl"
        completed = {row["id"] for row in read_jsonl(output)} if output.exists() and config.get("runtime", {}).get("resume") else set()
        selected_items = [runtime_by_id[item.id] if method in predicted_methods else item for item in items if item.id not in completed]
        rows = [run_pipeline(method, item, provider, config) for item in selected_items]
        write_jsonl(output, rows, append=bool(completed))
        print(f"{method}: wrote {len(rows)} rows -> {output}")


if __name__ == "__main__":
    main()
