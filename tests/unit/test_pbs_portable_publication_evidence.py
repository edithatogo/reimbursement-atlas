"""Check retained publication metadata offline, without re-attesting remote bytes."""

from pathlib import Path

from reimburse_atlas.pbs_publication_receipt import evidence_errors, load_receipt


def test_committed_publication_packet_has_valid_portable_proofs() -> None:
    root = Path(__file__).resolve().parents[2]
    receipt = load_receipt(root / "data/derived/publication/pbs_source_publication_receipt.json")
    assert receipt.publication_state == "published_verified"
    assert receipt.publication_blockers() == []
    assert evidence_errors(receipt, root) == []
