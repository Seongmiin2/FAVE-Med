from .vanilla_rag import run_vanilla_rag


def run_vanilla_controlled_rag(item, provider, config):
    result = run_vanilla_rag(item, provider, config)
    result.update(method="vanilla_controlled_rag", track="controlled")
    return result
