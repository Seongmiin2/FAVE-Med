from applicability_qa.retrieval import BM25Retriever, load_corpus


def test_bm25_retrieves_relevant_formula_card():
    corpus = load_corpus("data/telecom/corpus/evidence_corpus_seed.jsonl")
    retriever = BM25Retriever(corpus)
    cases = [
        ("Compute Shannon capacity from bandwidth and SNR", "shannon_capacity"),
        ("Compute FSPL at 2 km and 2400 MHz", "free_space_path_loss"),
        ("Find coherent BPSK BER from Eb N0", "bpsk_ber"),
        ("Find received power using Friis", "friis_received_power"),
    ]
    for query, source_id in cases:
        assert source_id in {row.source_id for row in retriever.retrieve(query, 5)}


def test_bm25_result_has_rank_score_and_provenance():
    row = BM25Retriever(load_corpus("data/telecom/corpus/evidence_corpus_seed.jsonl")).retrieve("Nyquist symbol rate", 1)[0]
    assert row.rank == 1
    assert row.score > 0
    assert row.source_id
    assert row.source_type
