from .demo_multi_executor import run_demo_multi_executor


def run_demo_oracle_executor(item, provider, config):
    result = run_demo_multi_executor(item, provider, config)
    result.update(formula_mode="oracle", is_primary_result=False)
    return result
