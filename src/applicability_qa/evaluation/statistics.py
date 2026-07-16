from __future__ import annotations

import math
import random


def exact_mcnemar(a: list[bool], b: list[bool]) -> dict[str, float | int]:
    if len(a) != len(b):
        raise ValueError("Paired outcomes must have equal length")
    b_only = sum((not x) and y for x, y in zip(a, b))
    a_only = sum(x and (not y) for x, y in zip(a, b))
    discordant = a_only + b_only
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(0, min(a_only, b_only) + 1)) / (2**discordant)
        p_value = min(1.0, 2 * tail)
    return {"a_correct_b_wrong": a_only, "a_wrong_b_correct": b_only, "discordant": discordant, "p_value": p_value}


def paired_bootstrap(a: list[bool], b: list[bool], *, resamples: int = 10_000, seed: int = 42, confidence: float = 0.95) -> dict[str, float | int]:
    if len(a) != len(b) or not a:
        raise ValueError("Non-empty paired outcomes of equal length are required")
    rng, n = random.Random(seed), len(a)
    differences = []
    for _ in range(resamples):
        indices = [rng.randrange(n) for _ in range(n)]
        differences.append(sum(int(b[i]) - int(a[i]) for i in indices) / n)
    differences.sort()
    alpha = 1 - confidence
    lower = differences[max(0, int(alpha / 2 * resamples))]
    upper = differences[min(resamples - 1, int((1 - alpha / 2) * resamples) - 1)]
    observed = sum(int(y) - int(x) for x, y in zip(a, b)) / n
    return {"difference_b_minus_a": observed, "ci_lower": lower, "ci_upper": upper, "confidence": confidence, "resamples": resamples, "seed": seed}


def holm_correction(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict[str, float | bool]]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    m, previous = len(ordered), 0.0
    result = {}
    still_rejecting = True
    for rank, (name, p_value) in enumerate(ordered, 1):
        adjusted = min(1.0, max(previous, (m - rank + 1) * p_value))
        previous = adjusted
        threshold = alpha / (m - rank + 1)
        reject = still_rejecting and p_value <= threshold
        if not reject:
            still_rejecting = False
        result[name] = {"raw_p": p_value, "adjusted_p": adjusted, "holm_threshold": threshold, "reject": reject}
    return result
