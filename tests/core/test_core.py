from applicability_qa.core.answer_parser import evaluate_answer
from applicability_qa.core.jsonl_utils import read_jsonl, write_jsonl
from applicability_qa.core.schemas import BenchmarkItem, GoldAnswer
from applicability_qa.pipelines.common import normalize


def test_schema_and_jsonl(tmp_path):
    item = BenchmarkItem(id="1", domain="medical", task_type="qa", question="q", gold_answer=GoldAnswer(value=2, output_type="integer"))
    path = tmp_path / "x.jsonl"
    write_jsonl(path, [item.model_dump()])
    assert list(read_jsonl(path))[0]["id"] == "1"


def test_final_value_not_intermediate_text():
    result = evaluate_answer({"answer": {"final_value": 10, "final_unit": "Mbps"}, "raw_response": {"reasoning": "999"}}, {"value": 10, "unit": "Mbps", "output_type": "telecom_quantity"}, "telecom")
    assert result["correct"]


def test_categorical():
    assert evaluate_answer({"answer": {"final_value": "Yes"}}, {"value": "yes", "unit": None, "output_type": "categorical"}, "medical")["correct"]


def test_dotted_answer_keys_are_normalized():
    item = BenchmarkItem(id="1", domain="telecom", task_type="qa", question="q", gold_answer=GoldAnswer(value=1, unit="bps", output_type="telecom_quantity"))
    result = normalize(item, "test", {"answer.final_value": 1, "answer.final_unit": "bps"})
    assert result["answer"] == {"final_value": 1, "final_unit": "bps"}
