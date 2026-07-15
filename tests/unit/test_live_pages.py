"""Tests for the deployed dashboard smoke contract."""

from __future__ import annotations

from urllib.parse import urlsplit

import pytest

from scripts import check_live_pages


def test_live_pages_accepts_project_prefixed_references(monkeypatch: pytest.MonkeyPatch) -> None:
    """A healthy project site and its critical data paths should pass."""
    root = "https://example.github.io/reimbursement-atlas/"
    html = b'<html><head><link rel="icon" href="/reimbursement-atlas/favicon.svg"></head></html>'

    def fake_fetch(url: str, attempts: int) -> tuple[int, bytes]:
        del attempts
        return (200, html) if url == root else (200, b"ok")

    monkeypatch.setattr(check_live_pages, "_fetch", fake_fetch)
    assert check_live_pages.validate_live_pages(root, attempts=1) == []


def test_live_pages_rejects_root_relative_references(monkeypatch: pytest.MonkeyPatch) -> None:
    """A deployment must not silently request assets from the domain root."""
    root = "https://example.github.io/reimbursement-atlas/"
    html = b'<html><script src="/_astro/client.js"></script></html>'

    def fake_fetch(url: str, attempts: int) -> tuple[int, bytes]:
        del attempts
        if urlsplit(url).path == "/reimbursement-atlas/":
            return 200, html
        return 200, b"ok"

    monkeypatch.setattr(check_live_pages, "_fetch", fake_fetch)
    errors = check_live_pages.validate_live_pages(root, attempts=1)
    assert errors == ["root-relative or malformed dashboard reference: /_astro/client.js"]
