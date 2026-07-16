# External-method reproduction boundary

The official CRAG and MedRaC sources were inspected and pinned in
`configs/reproductions/external_methods.yaml`. The local methods named
`crag_proxy` and `medrac_proxy` are not reported as official reproductions.

## CRAG

The official pipeline requires a trained T5-large retrieval evaluator, two
decision thresholds, correct/incorrect/ambiguous routing, passage
decomposition/recomposition, an external Google-search-compatible service,
and the original generator. The pinned repository contains no license file,
so its source is not copied into this repository. A faithful run must use an
untouched external checkout and separately obtained model/search credentials.

## MedRaC

The official Apache-2.0 implementation retrieves formula descriptions using
embeddings, asks the model to extract formula variables, generates calculation
code, and executes it. A faithful numerical reproduction additionally requires
the authors' cleaned benchmark/formula files and the configured model versions.
The local exact-ID medical executors are safer for the proposed method but are
not equivalent to MedRaC's model-generated Python and must not be substituted
when labeling a run as an official reproduction.

## Preparing untouched official checkouts

```powershell
python scripts/prepare_external_reproductions.py
```

External checkouts are operational dependencies, not project source. Results
must record repository commit, model snapshot, corpus hash, thresholds, search
backend, and prompt hash. Until those dependencies are supplied and the
official entry points run, the correct status is `reproduction_prepared`, not
`reproduced`.

## Development execution status

On 2026-07-16, the pinned MedRaC code completed a three-record development
subset using its Formula-RAG, structured extraction, generated-Python execution,
and regular evaluator. It scored 2/3. This establishes an executable partial
reproduction, not the paper's full multi-model result reproduction. See
`reports/PAID_DEVELOPMENT_REPRODUCTION_20260716.md`.

CRAG remains prepared but unexecuted because the required evaluator/generator
checkpoints, CUDA runtime, and Google-search-compatible credential are not
available in this workspace.
