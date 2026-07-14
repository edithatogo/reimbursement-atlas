# Deterministic candidate-only token overlap prototype.
# Python remains the auditable reference implementation.

def token_jaccard(left: String, right: String) -> Float64:
    """Return a whitespace-token Jaccard score for candidate prefiltering."""
    var left_tokens = left.split()
    var right_tokens = right.split()
    var left_count = 0
    var right_count = 0
    var common_count = 0

    for left_token in left_tokens:
        left_count += 1
        for right_token in right_tokens:
            if left_token == right_token:
                common_count += 1
                break
    for _ in right_tokens:
        right_count += 1

    var union_count = left_count + right_count - common_count
    if union_count == 0:
        return 0.0
    return Float64(common_count) / Float64(union_count)


def main():
    var score = token_jaccard("whole exome", "whole exome sequencing")
    assert score > 0.6
    print(score)
