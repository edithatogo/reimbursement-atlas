from scripts.make_mapping_private_enriched_cycle import build_enriched_cycle


def _base(family: str, count: int, hypothesis: str = "positive_candidate") -> list[dict]:
    return [
        {
            "case_id": f"{family}_{index}",
            "family": family,
            "left_code": f"L{index}",
            "right_code": f"R{index}",
            "right_source_id": "public",
            "proposed_label_hypothesis": hypothesis,
            "duplicate_group": f"{family}_{index}",
        }
        for index in range(count)
    ]


def test_private_enriched_cycle_preserves_family_quotas() -> None:
    base = [
        *_base("procedures_pathology", 200, "negative_candidate"),
        *_base("medicines", 400),
        *_base("genomics_coverage", 300),
        *_base("devices_other", 200),
    ]
    local = [
        {
            "candidate_id": f"cpt_{index}",
            "left_code": f"M{index}",
            "right_code": f"{index:05d}",
            "left_description": f"Procedure alpha {index}",
            "right_description": f"Procedure alpha {index}",
            "token_jaccard": 0.8,
        }
        for index in range(400)
    ]
    frame, private, summary = build_enriched_cycle(
        base_frame=base,
        local_cpt_candidates=local,
        mbs_bundle_sha256="a" * 64,
        cpt_archive_sha256="b" * 64,
    )
    assert len(frame) == 1500
    assert len(private) == 400
    assert summary["family_summary"]["procedures_pathology"]["available"] == 600
    assert all("description" not in row for row in frame)
