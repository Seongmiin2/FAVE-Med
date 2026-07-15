from ...core.answer_parser import evaluate_answer


def evaluate(item, prediction):
    return evaluate_answer(prediction, item.gold_answer.model_dump(), "medical")
