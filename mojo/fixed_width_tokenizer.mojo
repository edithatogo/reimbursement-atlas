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

def main():
    var sample = "ITEM|GROUP|FEE|DESCRIPTOR"
    print(count_pipes(sample))
