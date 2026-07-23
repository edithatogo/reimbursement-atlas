"""Local-only CPT descriptor enrichment for mapping candidate review."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from reimburse_atlas.crosswalk import jaccard_similarity, tokenise

EXPECTED_MEMBER = "PPRRVU2026_Jul_nonQPP.csv"
COPYRIGHT_MARKER = "CPT codes and descriptions only are copyright"


class CptEnrichmentError(ValueError):
    """Raised when local CPT evidence does not meet the expected contract."""


def build_local_cpt_candidates(
    *,
    cms_archive: Path,
    mbs_bundle: Path,
    minimum_score: float = 0.12,
    candidates_per_item: int = 3,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Build descriptor-bearing candidates for ignored local review storage."""
    cpt_rows, copyright_notice = _read_cpt_rows(cms_archive)
    mbs_rows = _read_jsonl(mbs_bundle)
    cpt_tokens = [set(tokenise(row["description"])) for row in cpt_rows]
    token_index: dict[str, set[int]] = defaultdict(set)
    for index, tokens in enumerate(cpt_tokens):
        for token in tokens:
            token_index[token].add(index)

    candidates: list[dict[str, object]] = []
    for mbs in mbs_rows:
        mbs_text = " ".join(
            str(mbs.get(field) or "") for field in ("item_label", "item_description", "domain")
        )
        mbs_tokens = set(tokenise(mbs_text))
        indexes: set[int] = set()
        for token in mbs_tokens:
            indexes.update(token_index.get(token, set()))
        scored = sorted(
            (
                (jaccard_similarity(mbs_tokens, cpt_tokens[index]), cpt_rows[index])
                for index in indexes
            ),
            key=lambda item: (-item[0], item[1]["code"]),
        )
        for score, cpt in scored[:candidates_per_item]:
            if score < minimum_score:
                continue
            identity = f"{mbs['item_code']}|{cpt['code']}|{score:.8f}"
            candidates.append({
                "schema_version": "local-cpt-enrichment-candidate-v1",
                "candidate_id": hashlib.sha256(identity.encode()).hexdigest()[:24],
                "left_source_id": "au_mbs",
                "left_code": mbs["item_code"],
                "left_description": mbs_text,
                "right_source_id": "us_cms_pfs_local_cpt",
                "right_code": cpt["code"],
                "right_description": cpt["description"],
                "token_jaccard": round(score, 8),
                "status": "hypothesis_requires_blinded_review",
            })

    candidates.sort(key=lambda row: str(row["candidate_id"]))
    summary: dict[str, object] = {
        "schema_version": "local-cpt-enrichment-summary-v1",
        "status": "ready_for_local_blinded_review" if candidates else "blocked_no_candidates",
        "source": {
            "source_id": "us_cms_pfs_rvu26c",
            "release": "RVU26C",
            "effective_period": "2026-07",
            "archive_sha256": _sha256(cms_archive),
            "archive_member": EXPECTED_MEMBER,
            "copyright_notice_sha256": hashlib.sha256(copyright_notice.encode("utf-8")).hexdigest(),
        },
        "mbs_bundle_sha256": _sha256(mbs_bundle),
        "cpt_record_count": len(cpt_rows),
        "mbs_record_count": len(mbs_rows),
        "candidate_count": len(candidates),
        "minimum_score": minimum_score,
        "candidates_per_item": candidates_per_item,
        "descriptor_storage": "ignored_local_only",
        "public_output_fields": [
            "source checksums",
            "release identity",
            "record counts",
            "candidate count",
            "method parameters",
        ],
        "restrictions": [
            "Do not commit or publish CPT descriptions.",
            "Candidate hypotheses are not mapping truth.",
            "A fresh blinded review and accountable adjudication are required.",
        ],
    }
    return candidates, summary


def _read_cpt_rows(archive: Path) -> tuple[list[dict[str, str]], str]:
    if not zipfile.is_zipfile(archive):
        message = "CMS PFS input is not a ZIP archive"
        raise CptEnrichmentError(message)
    with zipfile.ZipFile(archive) as package:
        if EXPECTED_MEMBER not in package.namelist():
            message = f"missing expected archive member: {EXPECTED_MEMBER}"
            raise CptEnrichmentError(message)
        text = package.read(EXPECTED_MEMBER).decode("utf-8-sig")
    lines = text.splitlines()
    notice = next((line for line in lines if COPYRIGHT_MARKER in line), "")
    if not notice:
        message = "CMS PFS copyright notice was not found"
        raise CptEnrichmentError(message)
    header_index = next(
        (index for index, line in enumerate(lines) if line.startswith("HCPCS,MOD,DESCRIPTION,")),
        None,
    )
    if header_index is None:
        message = "CMS PFS CSV header was not found"
        raise CptEnrichmentError(message)
    rows: list[dict[str, str]] = []
    for row in csv.DictReader(io.StringIO("\n".join(lines[header_index:]))):
        code = str(row.get("HCPCS") or "").strip()
        description = str(row.get("DESCRIPTION") or "").strip()
        if len(code) == 5 and code.isdigit() and description:
            rows.append({"code": code, "description": description})
    if not rows:
        message = "CMS PFS archive contained no numeric CPT records"
        raise CptEnrichmentError(message)
    return rows, notice


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        cast("dict[str, Any]", json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
