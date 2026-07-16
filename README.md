# Applicability-QA-Lab

FAVE-RAG의 증거 적용 가능성 검증과 DeMo-Med의 공식 분해·검증·결정론적 실행을 하나의 정량 QA 실험 프레임워크로 재구성한 프로젝트입니다. 원본 저장소와 원본 데이터는 수정하지 않습니다.

> The 10-item experiment is a feasibility pilot, not a definitive benchmark result.
> Executor-based historical methods use an oracle formula and therefore measure
> variable extraction plus deterministic execution under an upper-bound condition.
> Primary thesis results must use predicted-formula methods with no gold formula,
> answer, variable annotation, or evidence labels in runtime inputs.

## 연구 질문

증거 검증과 단계별 계산을 결합했을 때 정량 QA의 정확성과 강건성이 얼마나 개선되는지 비교합니다.

## 구조와 방법

`core`는 공통 스키마·파서·단위·지표를, `domains`는 telecom/medical 어댑터와 계산기를, `pipelines`는 LLM-only, Vanilla RAG, FAVE, DeMo, FAVE-DeMo를 담당합니다. 모든 결과는 동일한 JSONL 구조로 저장됩니다.

## 설치

Python 3.11 이상 설치 후 프로젝트 루트에서 실행합니다.

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

## 데이터 준비와 실험

기본 config는 비용 없는 mock provider를 사용합니다. 실제 호출 시 provider를 `openai`로 바꾸고 `.env`에 키를 설정합니다.

```powershell
python -m applicability_qa.cli.prepare --config configs/experiments/telecom_pilot.yaml
python -m applicability_qa.cli.run --config configs/experiments/telecom_pilot.yaml --method llm_only
python -m applicability_qa.cli.evaluate --config configs/experiments/telecom_pilot.yaml
```

일부 문항만 실행하려면 `--max-items 1` 또는 `--max-items 3`을 사용합니다. Mock 검증 후 OpenAI 3문항 실험은 다음 config로 준비되어 있습니다.

```powershell
python -m applicability_qa.cli.run --config configs/experiments/telecom_openai_3.yaml --max-items 3
python -m applicability_qa.cli.evaluate --config configs/experiments/telecom_openai_3.yaml
```

평가는 answer accuracy, parse success, abstention을 공통 산출하며 telecom 증거 지표와 medical 실행 지표는 후속 확장 지점입니다. 현재 결정론적 실행기는 Shannon/Friis/FSPL과 BMI/MAP/anion gap을 우선 지원합니다.

## 한계와 향후 계획

현재는 1차 통합 골격과 pilot 실행 범위입니다. 전체 의료 계산기, telecom 공식, evidence precision/recall/F1, 통계 검정, combined report를 순차 확장해야 합니다. 실제 실험 결과는 모델과 prompt version을 고정한 뒤 작성합니다.

## 출처

This repository integrates and refactors components from:

- FAVE-RAG: https://github.com/Seongmiin2/FAVE-RAG
- DeMo-Med: https://github.com/Seongmiin2/DeMo-Med
