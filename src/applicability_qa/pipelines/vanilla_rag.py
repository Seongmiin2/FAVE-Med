from .common import SYSTEM, context, normalize


def run_vanilla_rag(item, provider, config):
    ids = item.metadata.get("mixed_context")
    prompt = f"Question: {item.question}\nEvidence:\n{context(item, ids)}"
    return normalize(item, "vanilla_rag", provider.generate_json(SYSTEM, prompt))
