from .fave_demo import run_fave_demo


def run_fave_oracle_executor(item, provider, config):
    result = run_fave_demo(item, provider, config)
    result.update(formula_mode="oracle", is_primary_result=False)
    return result
