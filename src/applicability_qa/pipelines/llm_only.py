from .common import SYSTEM, normalize, question_prompt


def run_llm_only(item, provider, config):
    return normalize(item, "llm_only", provider.generate_json(SYSTEM, question_prompt(item)))
