"""Deterministic string prefiltering for crosswalk candidate generation.

This module provides a Jaccard/token-overlap prefilter that serves as the
Python baseline for future Mojo kernel optimisation (`mojo/fuzzy_join.mojo`).
"""

from __future__ import annotations

from reimburse_atlas.crosswalk import jaccard_similarity, normalise_text


def fuzzy_prefilter(
    left_labels: list[str],
    right_labels: list[str],
    *,
    threshold: float = 0.3,
    max_per_left: int = 10,
) -> list[tuple[int, int, float]]:
    """Return ``(left_idx, right_idx, score)`` tuples for token-overlap pairs.

    This is a deterministic, transparent prefilter designed to reduce the
    candidate crosswalk space before more expensive evidence methods run.
    """
    left_norm = [normalise_text(label) for label in left_labels]
    right_norm = [normalise_text(label) for label in right_labels]
    results: list[tuple[int, int, float]] = []

    for li, left in enumerate(left_norm):
        left_tokens = tuple(left.split())
        scored: list[tuple[float, int]] = []
        for ri, right in enumerate(right_norm):
            right_tokens = tuple(right.split())
            score = jaccard_similarity(left_tokens, right_tokens)
            if score >= threshold:
                scored.append((score, ri))
        scored.sort(key=lambda x: (-x[0], x[1]))
        for score, ri in scored[:max_per_left]:
            results.append((li, ri, score))

    return sorted(results, key=lambda x: (-x[2], x[0], x[1]))
