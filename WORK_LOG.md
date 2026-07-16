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
- `python -m pytest -q`: `10 passed`
- Telecom 첫 pilot 문항 adapter 변환: 성공
- BMI 직접 실행: `22.857142857142858 kg/m^2`
- mock 기반 `llm_only`, `vanilla_rag`, `fave_silent`, `demo_multi_executor`, `fave_demo`: Telecom 10문항 전체 실행 성공
- 5개 mock 결과의 최상위 JSONL 스키마 일치 확인
- 10개 Telecom pilot 공식의 결정론적 실행 성공
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

실행 순서는 `llm_only`, `vanilla_rag`, `fave_silent`, `demo_multi_executor`, `fave_demo`로 config에 고정했다. 첫 3문항 실제 API 호출과 평가를 완료했다.

## 6. 남은 문제

- Telecom mock 10문항은 5개 비교 방법 모두 실행 성공했으며 accuracy와 parse success rate가 1.0이다.
- FAVE 계열 mock의 invalid evidence precision/recall/F1은 1.0이고 valid evidence false rejection rate는 0.0이다.
- OpenAI 3문항과 10문항 전체 pilot 실행을 완료했다. 다음 단계는 독립 검수된 50–100문항 확장이다.
- Mock 결과는 실행·스키마·평가기 회귀 검증용 fixture이며 실제 모델 성능 결과로 해석하면 안 된다.
- 지원 범위는 현재 pilot 10문항 공식에 맞춰져 있으므로 새로운 Telecom 공식이 추가되면 executor도 함께 확장해야 한다.

## 7. 실제 OpenAI 3문항 결과

`gpt-4o`, temperature 0, prompt version v1로 Telecom 첫 3문항을 실행했다. 총 15개 저장 결과에서 parse failure, executor failure, abstention은 없었다.

| Method | Accuracy | Parse success | Invalid evidence F1 | Valid false rejection |
|---|---:|---:|---:|---:|
| llm_only | 0.667 | 1.000 | 0.000 | 0.000 |
| vanilla_rag | 0.667 | 1.000 | 0.000 | 0.000 |
| fave_silent | 0.667 | 1.000 | 1.000 | 0.000 |
| demo_multi_executor | 1.000 | 1.000 | 0.000 | 0.000 |
| fave_demo | 1.000 | 1.000 | 1.000 | 0.000 |

표본이 3문항뿐이므로 성능 결론이 아니라 전체 10문항 실험 전 실행 검증 결과로 해석한다. 저장된 최종 결과 기준 token 합계는 input 2,135, output 708이며, evidence 판정 중간 호출 token은 최종 행 합계에 포함되지 않는다.

## 8. 실제 OpenAI 10문항 확대 결과

Telecom pilot 전체 10문항과 다섯 방법으로 50개 최종 결과를 생성했다. 직접 답변 방법은 각각 5/10, executor 방법은 각각 10/10을 기록했다. FAVE evidence 판정은 precision 1.0, recall 0.7, F1 0.824였다. Paired exact McNemar 비교에서 executor 방법과 LLM-only 간 p-value는 0.0625로, 작은 표본에서 5% 유의수준을 충족하지 않았다.

Executor 방법에는 benchmark의 gold formula가 제공되므로 이 결과는 end-to-end 공식 선택 성능이 아니라 oracle-formula 조건의 분해·결정론적 실행 상한선이다. 상세 결과와 한계는 `EXPERIMENT_REPORT.md`에 기록했다.

## 9. 원본 출처

This repository integrates and refactors components from:

- FAVE-RAG: https://github.com/Seongmiin2/FAVE-RAG
- DeMo-Med: https://github.com/Seongmiin2/DeMo-Med
