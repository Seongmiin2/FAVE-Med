# Telecom OpenAI Pilot Experiment Report

## Experiment setup

- Date: 2026-07-16
- Benchmark: `data/telecom/benchmark/fave_bench_10.jsonl`
- Items: 10
- Model: `gpt-4o`
- Temperature: 0
- Prompt version: v1
- Compared methods: LLM-only, Vanilla RAG, FAVE silent, DeMo multi + executor, FAVE-DeMo
- Final answer source: `answer.final_value` and `answer.final_unit` only

The run produced 50 final records. All records parsed successfully; there were no final executor failures or abstentions. The saved final records contain 6,968 input tokens and 2,417 output tokens. Evidence-classification calls are intermediate calls and are not included in that saved-row token sum.

## Results

| Method | Correct | Accuracy | 95% Wilson CI | Trap hit | Invalid evidence P/R/F1 | Valid false rejection |
|---|---:|---:|---:|---:|---:|---:|
| LLM-only | 5/10 | 0.50 | [0.237, 0.763] | 0.00 | N/A | N/A |
| Vanilla RAG | 5/10 | 0.50 | [0.237, 0.763] | 0.10 | N/A | N/A |
| FAVE silent | 5/10 | 0.50 | [0.237, 0.763] | 0.10 | 1.00 / 0.70 / 0.824 | 0.00 |
| DeMo multi + executor | 10/10 | 1.00 | [0.722, 1.000] | 0.00 | N/A | N/A |
| FAVE-DeMo | 10/10 | 1.00 | [0.722, 1.000] | 0.00 | 1.00 / 0.70 / 0.824 | 0.00 |

Paired exact McNemar comparisons:

| Comparison | Improved / regressed discordant pairs | Exact p-value |
|---|---:|---:|
| DeMo multi + executor vs LLM-only | 5 / 0 | 0.0625 |
| FAVE-DeMo vs LLM-only | 5 / 0 | 0.0625 |
| FAVE-DeMo vs Vanilla RAG | 5 / 0 | 0.0625 |
| FAVE silent vs Vanilla RAG | 0 / 0 | 1.0000 |

## Interpretation

The deterministic execution stage is promising in this pilot. It corrected arithmetic and formula-application failures on FSPL, Rayleigh outage, BPSK BER, MIMO capacity, and Friis received power. Both executor methods solved all ten items, while the three direct-answer methods solved five.

Evidence filtering alone did not improve answer accuracy: FAVE silent and Vanilla RAG both achieved 0.50 and had identical per-item correctness. FAVE classified rejected evidence with perfect precision but only 0.70 recall. This indicates that applicability classification is partially working, but filtering alone does not resolve arithmetic or formula execution errors.

The executor comparison does not yet demonstrate end-to-end formula selection. `demo_multi_executor` and `fave_demo` receive the benchmark formula stored in `BenchmarkItem.formula`, so their 1.00 accuracy measures variable extraction plus deterministic execution under an oracle-formula condition. This is a useful upper-bound and component ablation, not a fair end-to-end comparison against LLM-only.

The apparent 0.50 absolute accuracy improvement is not significant at the conventional 0.05 level in this ten-item paired sample (`p=0.0625`). Confidence intervals are broad. The experiment supports continuing the study, but it is too small for a strong performance claim.

## Threats to validity

- Only ten manually curated Telecom questions are included.
- The same model and a single deterministic decoding setting were used once; there are no repeated runs or model comparisons.
- Executor methods use an oracle formula supplied by benchmark metadata.
- The benchmark covers ten formula families but not the wider distribution of Telecom quantitative QA.
- Prompt wording and unit aliases were refined during pilot validation. Results should be rerun from clean output directories after any further prompt or evaluator change.
- Token accounting excludes intermediate evidence-classification calls, so it cannot yet support a complete cost comparison.

## Recommended next experiment

1. Expand to at least 50–100 independently reviewed questions, stratified by formula family and invalid-evidence type.
2. Add formula selection accuracy and run executor methods in both oracle-formula and predicted-formula conditions.
3. Repeat each stochastic condition with at least three seeds or use deterministic decoding across multiple models.
4. Pre-register the evaluator, unit aliases, prompts, and tolerances before the full run.
5. Save usage for every intermediate call to compare total latency and cost.
6. Report paired bootstrap confidence intervals and exact McNemar tests with multiplicity-aware interpretation.

## Reproduction

```powershell
python -m applicability_qa.cli.run `
  --config configs/experiments/telecom_openai_10.yaml `
  --max-items 10

python -m applicability_qa.cli.evaluate `
  --config configs/experiments/telecom_openai_10.yaml
```

Generated local artifacts:

```text
outputs/telecom/openai_10/*.jsonl
results/telecom/openai_10/per_item.jsonl
results/telecom/openai_10/summary.csv
results/telecom/openai_10/report.md
```
