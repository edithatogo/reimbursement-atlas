# Deterministic candidate-only token overlap prototype.
# Python remains the auditable reference implementation.


def contains_token(tokens: List[String], value: String) -> Bool:
    for token in tokens:
        if token == value:
            return True
    return False


def unique_tokens(text: String) -> List[String]:
    var unique = List[String]()
    for token in text.split():
        var token_text = String(token)
        if not contains_token(unique, token_text):
            unique.append(token_text)
    return unique.copy()

def token_jaccard(left: String, right: String) -> Float64:
    """Return a whitespace-token Jaccard score for candidate prefiltering."""
    # Keep this bounded and compiler-compatible until the pinned Mojo baseline
    # exposes a stable native set type.
    var left_set = unique_tokens(left)
    var right_set = unique_tokens(right)
    var intersection_count = 0
    for token in left_set:
        if contains_token(right_set, token):
            intersection_count += 1
    var union_count = len(left_set) + len(right_set) - intersection_count
    if union_count == 0:
        return 0.0
    return Float64(intersection_count) / Float64(union_count)


def main():
    var score = token_jaccard("whole exome", "whole exome sequencing")
    assert score > 0.66 and score < 0.67
    assert token_jaccard("a a", "a b") > 0.49 and token_jaccard("a a", "a b") < 0.51
    print(score)
