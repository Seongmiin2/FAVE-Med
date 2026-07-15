from .common import SYSTEM, context, normalize


def run_demo(item, provider, config):
    raw = provider.generate_json(SYSTEM, f"Question: {item.question}\nContext:\n{context(item)}\nExtract variables, verify units and conditions, then answer.")
    return normalize(item, "demo", raw)
