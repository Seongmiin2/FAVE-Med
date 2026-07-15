from .common import SYSTEM, normalize


def run_llm_only(item, provider, config):
    return normalize(item, "llm_only", provider.generate_json(SYSTEM, item.question))
