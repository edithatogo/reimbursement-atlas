from __future__ import annotations

import pytest

from scripts.zenodo_deposition import validate_api_url


@pytest.mark.parametrize(
    "url",
    [
        "http://zenodo.org/api",
        "https://example.com/api",
        "https://zenodo.org/api?token=secret",
        "file:///api",
    ],
)
def test_api_url_rejects_token_exfiltration_targets(url: str) -> None:
    with pytest.raises(ValueError, match="Zenodo API URL"):
        validate_api_url(url)


@pytest.mark.parametrize(
    "url",
    ["https://zenodo.org/api", "https://sandbox.zenodo.org/api/"],
)
def test_api_url_accepts_official_endpoints(url: str) -> None:
    assert validate_api_url(url).endswith("/api")
