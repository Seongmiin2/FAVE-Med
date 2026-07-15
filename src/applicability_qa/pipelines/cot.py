from .common import SYSTEM, normalize


def run_cot(item, provider, config):
    prompt = f"{item.question}\nReason step by step internally, but return only the final structured JSON."
    return normalize(item, "cot", provider.generate_json(SYSTEM, prompt))
