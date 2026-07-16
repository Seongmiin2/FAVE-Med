# telecom_end_to_end_mock_v3 report

Mock results validate integration only; they are not research performance evidence.

| Method | N | Accuracy | Parse success | Formula Acc@1 | Retrieval Recall@k |
|---|---:|---:|---:|---:|---:|
| fave_retrieval | 10 | 1.000 | 1.000 | 0.000 | 1.000 |
| fave_retrieval_predicted_executor | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| vanilla_retrieval_predicted_executor | 10 | 1.000 | 1.000 | 1.000 | 1.000 |
| vanilla_retrieval_rag | 10 | 1.000 | 1.000 | 0.000 | 1.000 |

Exact McNemar comparisons had no discordant pairs (`p=1.0`). Paired bootstrap differences were 0.0 with 95% CI `[0.0, 0.0]`; these fixture statistics have no inferential research meaning.
