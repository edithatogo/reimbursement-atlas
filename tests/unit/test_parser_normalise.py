from reimburse_atlas.parsers.normalise import parse_amount


def test_parse_amount_rejects_non_finite_values() -> None:
    for value in ("Infinity", "-Infinity", "NaN", float("inf"), float("nan")):
        assert parse_amount(value) is None


def test_parse_amount_preserves_finite_values() -> None:
    assert parse_amount("$1,234.56") == 1234.56
