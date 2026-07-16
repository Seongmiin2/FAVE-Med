"""Named comparison baselines.

These wrappers intentionally reuse the same retrieval/provider infrastructure so
comparisons differ by decision policy rather than by hidden corpus changes.
They are proxy implementations, not reproductions of third-party repositories.
"""

from .fave_retrieval import run_fave_retrieval
from .fave_retrieval_predicted_executor import run_fave_retrieval_predicted_executor
from .medical_predicted_executor import run_medical_predicted_executor
from .medical_retrieval import run_medical_fave_retrieval, run_medical_vanilla_retrieval
from .vanilla_retrieval_rag import run_vanilla_retrieval_rag


run_relevance_baseline = run_vanilla_retrieval_rag
run_factuality_baseline = run_fave_retrieval
run_crag_proxy = run_fave_retrieval_predicted_executor
run_medical_open_book = run_medical_vanilla_retrieval
run_medical_factuality_baseline = run_medical_fave_retrieval
run_medrac_proxy = run_medical_predicted_executor
