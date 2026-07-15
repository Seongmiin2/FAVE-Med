# Applicability-QA-Lab 작업 정리

## 1. 목표

FAVE-RAG의 증거 적용 가능성 검증과 DeMo-Med의 공식 분해·검증·결정론적 실행을 하나의 정량 QA 실험 프레임워크로 통합했다. 기존 `FAVE-RAG`, `DeMo-Med` 저장소와 원본 데이터는 수정하지 않았다.

## 2. 현재 구현 상태

### 공통 계층

- Pydantic 기반 `BenchmarkItem`, `GoldAnswer`, `FormulaSpec`, `EvidenceItem`
- JSONL 읽기·쓰기 및 잘못된 JSONL 위치 보고
- 숫자, 날짜, 범주형, Telecom 수량 답안 평가
- 단위 정규화 및 rate/frequency/power 단위 변환
- Mock/OpenAI provider 인터페이스
- config, model, seed, temperature, prompt version 기록 구조

답안 평가는 자유 텍스트의 첫 번째 숫자를 사용하지 않는다. 반드시 아래 필드만 평가한다.

```text
answer.final_value
answer.final_unit
```

### 도메인 계층

- FAVE Telecom pilot JSONL을 공통 `BenchmarkItem`으로 변환
- DeMo-Med CSV를 공통 `BenchmarkItem`으로 변환
- Telecom evidence accepted/rejected 결과 기록
- Medical BMI, MAP, Anion Gap 실행기
- Telecom Shannon capacity, spectral efficiency, Friis, FSPL 실행기

### 파이프라인

- `llm_only`
- `cot`
- `vanilla_rag`
- `fave`
- `fave_silent`
- `demo`
- `demo_multi_executor`
- `fave_demo`

모든 파이프라인은 동일한 JSONL 키를 사용한다.

```text
id, domain, method, model, prompt_version
answer, abstain, abstain_reason
accepted_evidence_ids, rejected_evidence_ids
extracted_variables, verification, execution
usage, raw_response
```

### CLI

- config 기반 데이터 검증, 실행, 평가, 보고서 생성
- `--method`로 단일 방법 선택
- `--max-items 1` 또는 `--max-items 3`으로 부분 실행
- 기존 출력 ID를 건너뛰는 resume 지원
- API 오류와 실행기 오류를 명시적인 abstention으로 저장

## 3. 검증 결과

- `python -m pip install -e .`: 성공
- package import 및 전체 source compile: 성공
- `TODO`, `FIXME`, `NotImplementedError`, 임시 `pass`, 빈 `...`: 없음
- `python -m pytest -q`: `8 passed`
- Telecom 첫 pilot 문항 adapter 변환: 성공
- BMI 직접 실행: `22.857142857142858 kg/m^2`
- mock 기반 `llm_only`, `vanilla_rag`, `fave`, `demo`, `fave_demo`: 한 문항 실행 성공
- 5개 mock 결과의 최상위 JSONL 스키마 일치 확인
- `--max-items 1`, `--max-items 3` 동작 확인

## 4. 평가 지표

현재 평가기는 다음 지표를 출력한다.

- Accuracy
- Parse success rate
- Abstention rate
- Trap hit rate
- Invalid evidence precision
- Invalid evidence recall
- Invalid evidence F1
- Valid evidence false rejection rate

결과 파일은 다음과 같다.

```text
results/telecom/per_item.jsonl
results/telecom/summary.csv
results/telecom/report.md
```

`outputs/`, `results/`는 재생성 가능한 산출물이므로 Git에서 제외한다.

## 5. 실행 방법

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest -q
```

Mock 한 문항 실행:

```powershell
python -m applicability_qa.cli.run `
  --config configs/experiments/telecom_pilot.yaml `
  --method llm_only `
  --max-items 1

python -m applicability_qa.cli.evaluate `
  --config configs/experiments/telecom_pilot.yaml
```

OpenAI 3문항 실험 준비 명령:

```powershell
python -m applicability_qa.cli.run `
  --config configs/experiments/telecom_openai_3.yaml `
  --max-items 3

python -m applicability_qa.cli.evaluate `
  --config configs/experiments/telecom_openai_3.yaml
```

실행 순서는 `llm_only`, `vanilla_rag`, `fave_silent`, `demo_multi_executor`, `fave_demo`로 config에 고정했다. 실제 API 호출은 아직 수행하지 않았다.

## 6. 남은 문제

- Mock provider는 첫 Telecom 문항 중심 fixture이므로 여러 공식의 변수 추출 mock을 추가해야 한다.
- 10문항 전체 FAVE-DeMo 실행 전 Telecom 공식 executor 지원 범위를 확장해야 한다.
- `demo_multi_executor`의 mock 3문항 실행에서는 첫 문항만 성공하고 나머지 두 문항은 안전하게 abstain했다.
- OpenAI 3문항 실험은 실행 가능하지만 API 키와 비용 확인 후 수행해야 한다.
- Telecom 10문항 중 LLM-only, Vanilla RAG, FAVE 계열은 실행 가능하다. 결정론적 executor를 포함한 전체 비교는 공식 지원 범위 확장 후 진행하는 것이 적절하다.

## 7. 원본 출처

This repository integrates and refactors components from:

- FAVE-RAG: https://github.com/Seongmiin2/FAVE-RAG
- DeMo-Med: https://github.com/Seongmiin2/DeMo-Med
