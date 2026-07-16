# Method matrix

| Method | Gold formula/entities | Context | Primary |
|---|---|---|---|
| llm_only / cot | no | none | baseline |
| vanilla_rag / vanilla_retrieval_rag | no | controlled/retrieved | baseline |
| fave / fave_retrieval | no | controlled/retrieved | baseline |
| demo_multi_executor / fave_demo | formula: yes | controlled | no, oracle pilot |
| demo_oracle_executor / fave_oracle_executor | formula: yes | controlled | no, upper bound |
| demo_predicted_executor / fave_predicted_executor | no | controlled | yes |
| vanilla_retrieval_predicted_executor | no | retrieved | yes, baseline |
| fave_retrieval_predicted_executor | no | retrieved | yes |
| medical_predicted_executor and retrieval variants | no | none/retrieved | yes |
| typed FAVE-DeMo variants | no | retrieved | yes, proposed |

`uses_gold_entities=false` for all primary runtime paths. Evaluators alone read gold annotations.
