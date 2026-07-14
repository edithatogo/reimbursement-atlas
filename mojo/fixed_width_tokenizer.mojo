# Fixed-width/TXT parsing smoke kernel for Reimbursement Atlas.
#
# This is intentionally small: Python remains the reference implementation,
# while Mojo kernels are added only where profiling justifies them.

def count_pipes(line: String) -> Int:
    var count = 0
    for i in range(line.byte_length()):
        if line[byte=i] == "|":
            count += 1
    return count


def fixed_width_tokenize(line: String, widths: List[Int]) -> List[String]:
    """Return trimmed byte slices using the same semantics as the Python parser."""
    var tokens = List[String]()
    var pos = 0
    for width in widths:
        tokens.append(String(line[byte=pos : pos + width].strip()))
        pos += width
    return tokens.copy()

def main():
    var sample = "ITEM|GROUP|FEE|DESCRIPTOR"
    var tokens = fixed_width_tokenize("ABCDE12345", [5, 5])
    assert tokens[0] == "ABCDE"
    assert tokens[1] == "12345"
    print(count_pipes(sample))
