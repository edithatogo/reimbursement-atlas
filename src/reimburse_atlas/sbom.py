"""Minimal CycloneDX-compatible SBOM generation for repo artefacts."""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import NAMESPACE_URL, uuid5

_PEP508_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def build_python_sbom(root: Path) -> dict[str, Any]:
    """Build a minimal CycloneDX 1.6 SBOM for Python dependencies."""
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    lock_packages = _uv_lock_packages(root / "uv.lock")
    components: list[dict[str, Any]] = []
    for package in lock_packages:
        component = {
            "type": "library",
            "name": package["name"],
            "version": package.get("version", ""),
            "bom-ref": f"pkg:pypi/{package['name']}@{package.get('version', '')}",
            "purl": f"pkg:pypi/{package['name']}@{package.get('version', '')}",
        }
        if hashes := package.get("hashes"):
            component["hashes"] = hashes
        components.append(component)
    if not components:
        components = [
            {
                "type": "library",
                "name": dependency_name(spec),
                "bom-ref": f"pkg:pypi/{dependency_name(spec)}",
                "scope": "required",
            }
            for spec in pyproject.get("project", {}).get("dependencies", [])
        ]
    return _bom(
        root=root,
        name="reimbursement-atlas-python",
        version=pyproject.get("project", {}).get("version", "0.0.0"),
        components=sorted(components, key=lambda item: (item["name"], item.get("version", ""))),
        ecosystem="python",
    )


def build_dashboard_sbom(root: Path) -> dict[str, Any]:
    """Build a minimal CycloneDX 1.6 SBOM for dashboard npm dependencies."""
    lock_path = root / "apps" / "dashboard" / "package-lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    packages = lock.get("packages", {})
    components: list[dict[str, Any]] = []
    for location, package in packages.items():
        if not location.startswith("node_modules/"):
            continue
        name = package.get("name") or location.removeprefix("node_modules/")
        version = str(package.get("version", ""))
        component: dict[str, Any] = {
            "type": "library",
            "name": name,
            "version": version,
            "bom-ref": f"pkg:npm/{name}@{version}",
            "purl": f"pkg:npm/{name}@{version}",
        }
        if integrity := package.get("integrity"):
            component["properties"] = [{"name": "npm:integrity", "value": integrity}]
        if license_name := package.get("license"):
            component["licenses"] = [{"license": {"name": license_name}}]
        components.append(component)
    package = packages.get("", {})
    return _bom(
        root=root,
        name="reimbursement-atlas-dashboard",
        version=str(package.get("version", "0.0.0")),
        components=sorted(components, key=lambda item: (item["name"], item.get("version", ""))),
        ecosystem="npm",
    )


def write_sbom(payload: dict[str, Any], path: Path) -> Path:
    """Write a deterministic SBOM payload."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def sbom_summary(payload: dict[str, Any]) -> dict[str, object]:
    """Return high-level SBOM metadata for dashboards and release checks."""
    components_raw = payload.get("components", [])
    components = (
        cast("list[dict[str, Any]]", components_raw) if isinstance(components_raw, list) else []
    )
    metadata = payload.get("metadata", {})
    metadata_dict = cast("dict[str, Any]", metadata) if isinstance(metadata, dict) else {}
    component = metadata_dict.get("component", {})
    component_dict = cast("dict[str, Any]", component) if isinstance(component, dict) else {}
    return {
        "name": component_dict.get("name", "unknown"),
        "ecosystem": _property(payload, "reimbursement-atlas:ecosystem"),
        "component_count": len(components),
        "spec_version": payload.get("specVersion", ""),
        "bom_format": payload.get("bomFormat", ""),
        "sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
    }


def dependency_name(spec: str) -> str:
    """Extract a package name from a PEP 508 dependency string."""
    match = _PEP508_NAME_RE.match(spec)
    if match is None:
        return spec
    return match.group(1).replace("_", "-").lower()


def _bom(
    *,
    root: Path,
    name: str,
    version: str,
    components: list[dict[str, Any]],
    ecosystem: str,
) -> dict[str, Any]:
    now = datetime.now(tz=UTC).replace(microsecond=0).isoformat()
    serial = uuid5(NAMESPACE_URL, f"https://example.invalid/{name}/{version}/{ecosystem}")
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{serial}",
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "reimbursement-atlas internal SBOM generator",
                        "version": "0.1.0",
                    }
                ]
            },
            "component": {"type": "application", "name": name, "version": version},
            "properties": [
                {"name": "reimbursement-atlas:ecosystem", "value": ecosystem},
                {"name": "reimbursement-atlas:source-root", "value": root.name},
            ],
        },
        "components": components,
    }


def _uv_lock_packages(lock_path: Path) -> list[dict[str, Any]]:
    if not lock_path.exists():
        return []
    data = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    packages: list[dict[str, Any]] = []
    for package in data.get("package", []):
        name = str(package.get("name", "")).lower()
        if not name or name == "reimbursement-atlas":
            continue
        hashes: list[dict[str, str]] = []
        for wheel in package.get("wheels", []):
            if raw_hash := wheel.get("hash"):
                algorithm, _, content = str(raw_hash).partition(":")
                hashes.append({"alg": algorithm.upper(), "content": content})
        packages.append({
            "name": name,
            "version": str(package.get("version", "")),
            "hashes": hashes,
        })
    return packages


def _property(payload: dict[str, Any], name: str) -> str:
    for prop in payload.get("metadata", {}).get("properties", []):
        if prop.get("name") == name:
            return str(prop.get("value", ""))
    return ""
