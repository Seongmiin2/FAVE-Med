from .fave import run_fave


def run_fave_controlled(item, provider, config):
    result = run_fave(item, provider, config)
    result.update(method="fave_controlled", track="controlled")
    return result
