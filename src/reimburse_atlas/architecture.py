"""Architecture-boundary analysis for the repository's Python package.

The analyser is intentionally lightweight and static.  It records internal
``reimburse_atlas`` import edges, maps modules onto architectural layers, checks
that lower layers do not depend on higher layers, and detects internal import
cycles.  It is designed as a generated quality gate rather than a replacement
for a full import linter.
"""

from __future__ import annotations

import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from reimburse_atlas.io import write_csv, write_jsonl
from reimburse_atlas.registry import project_root

ArchitectureLayer = Literal[
    "foundation",
    "parsing",
    "analysis",
    "orchestration",
    "interface",
    "unknown",
]
ImportKind = Literal["import", "from"]
PolicyStatus = Literal["pass", "fail", "warn"]

_LAYER_ORDER: dict[ArchitectureLayer, int] = {
    "foundation": 0,
    "parsing": 1,
    "analysis": 2,
    "orchestration": 3,
    "interface": 4,
    "unknown": 5,
}
_LAYER_BY_ROOT_MODULE: dict[str, ArchitectureLayer] = {
    "models": "foundation",
    "contracts": "foundation",
    "io": "foundation",
    "registry": "foundation",
    "quality": "foundation",
    "validation": "foundation",
    "licensing": "foundation",
    "repo_policy": "foundation",
    "toolchain": "foundation",
    "parsers": "parsing",
    "terminologies": "foundation",
    "snapshots": "parsing",
    "local_sources": "parsing",
    "analysis": "analysis",
    "crosswalk": "analysis",
    "demonstrators": "analysis",
    "graph": "analysis",
    "gold_standard": "analysis",
    "policy_metrics": "analysis",
    "review_queue": "analysis",
    "scoring": "analysis",
    "vector_index": "analysis",
    "warehouse": "analysis",
    "acquisition_pack": "orchestration",
    "action_pins": "orchestration",
    "adapters": "orchestration",
    "architecture": "orchestration",
    "automation": "orchestration",
    "datalake": "orchestration",
    "ingest": "orchestration",
    "ingestion": "orchestration",
    "local_quality": "orchestration",
    "publication": "orchestration",
    "protocols": "orchestration",
    "release_readiness": "orchestration",
    "sbom": "orchestration",
    "osf": "orchestration",
    "research_package": "orchestration",
    "source_downloads": "orchestration",
    "source_validation": "orchestration",
    "source_contracts": "orchestration",
    "github_project": "orchestration",
    "final_handoff": "orchestration",
    "data_quality": "orchestration",
    "data_dictionary": "orchestration",
    "evidence_readiness": "orchestration",
    "roadmap_linkages": "orchestration",
    "source_drift": "orchestration",
    "api": "interface",
    "cli": "interface",
    "mcp_server": "interface",
}


@dataclass(frozen=True)
class ImportEdgeRecord:
    """One internal import edge between modules."""

    source_module: str
    target_module: str
    source_layer: ArchitectureLayer
    target_layer: ArchitectureLayer
    import_kind: ImportKind
    line: int
    allowed: bool
    reason: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class LayerPolicyRecord:
    """One architectural layer-policy check."""

    id: str
    source_layer: ArchitectureLayer
    target_layer: ArchitectureLayer
    status: PolicyStatus
    edge_count: int
    evidence: str
    recommended_action: str

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureSummary:
    """Summary of architecture-boundary checks."""

    schema_version: str
    module_count: int
    edge_count: int
    layer_violation_count: int
    unknown_layer_count: int
    internal_cycle_count: int
    architecture_ready: bool

    def as_row(self) -> dict[str, object]:
        """Return a CSV/JSON-safe row."""
        return asdict(self)


@dataclass(frozen=True)
class ArchitectureReport:
    """Full architecture-boundary report."""

    edges: tuple[ImportEdgeRecord, ...]
    layer_policies: tuple[LayerPolicyRecord, ...]
    cycles: tuple[tuple[str, ...], ...]
    summary: ArchitectureSummary


def module_name_for_path(path: Path, src_root: Path) -> str:
    """Return the importable module name for a Python source path."""
    relative = path.relative_to(src_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def layer_for_module(module: str) -> ArchitectureLayer:
    """Map an internal module to its architectural layer."""
    parts = module.split(".")
    if module == "reimburse_atlas":
        return "foundation"
    if len(parts) < 2 or parts[0] != "reimburse_atlas":
        return "unknown"
    if module == "reimburse_atlas.parsers.normalise":
        return "foundation"
    if len(parts) == 2 and parts[1] == "__init__":
        return "foundation"
    return _LAYER_BY_ROOT_MODULE.get(parts[1], "unknown")


def scan_import_edges(root: Path | None = None) -> list[ImportEdgeRecord]:
    """Scan the Python package and return internal import edges."""
    repo = root or project_root()
    src_root = repo / "src"
    package_root = src_root / "reimburse_atlas"
    edges: list[ImportEdgeRecord] = []
    for path in sorted(package_root.rglob("*.py")):
        module = module_name_for_path(path, src_root)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = _normalise_internal_target(alias.name)
                    if target is not None:
                        edges.append(_edge(module, target, "import", node.lineno))
            elif isinstance(node, ast.ImportFrom):
                target = _resolve_import_from(module, node)
                if target is not None:
                    edges.append(_edge(module, target, "from", node.lineno))
    return _deduplicate_edges(edges)


def build_architecture_report(root: Path | None = None) -> ArchitectureReport:
    """Build the architecture report from source imports."""
    repo = root or project_root()
    edges = scan_import_edges(repo)
    modules = _internal_modules(repo)
    policies = build_layer_policy_records(edges)
    cycles = tuple(tuple(cycle) for cycle in find_import_cycles(edges))
    unknown_layer_count = sum(1 for module in modules if layer_for_module(module) == "unknown")
    layer_violation_count = sum(1 for edge in edges if not edge.allowed)
    summary = ArchitectureSummary(
        schema_version="architecture-boundaries-v1",
        module_count=len(modules),
        edge_count=len(edges),
        layer_violation_count=layer_violation_count,
        unknown_layer_count=unknown_layer_count,
        internal_cycle_count=len(cycles),
        architecture_ready=layer_violation_count == 0 and unknown_layer_count == 0 and not cycles,
    )
    return ArchitectureReport(
        edges=tuple(edges),
        layer_policies=tuple(policies),
        cycles=cycles,
        summary=summary,
    )


def build_layer_policy_records(edges: list[ImportEdgeRecord]) -> list[LayerPolicyRecord]:
    """Summarise layer-to-layer policy outcomes."""
    records: list[LayerPolicyRecord] = []
    layers: tuple[ArchitectureLayer, ...] = (
        "foundation",
        "parsing",
        "analysis",
        "orchestration",
        "interface",
        "unknown",
    )
    for source in layers:
        for target in layers:
            matching = [
                edge
                for edge in edges
                if edge.source_layer == source and edge.target_layer == target
            ]
            if not matching and "unknown" not in {source, target}:
                continue
            violation_count = sum(1 for edge in matching if not edge.allowed)
            status: PolicyStatus = "pass"
            action = "No action required."
            evidence = f"{len(matching)} observed import edge(s)."
            if "unknown" in {source, target}:
                status = "warn" if matching else "pass"
                action = "Assign unknown modules to a named architecture layer."
            if violation_count:
                status = "fail"
                action = "Move shared logic downward or introduce a boundary-facing adapter."
                evidence = f"{violation_count} violation(s) across {len(matching)} edge(s)."
            records.append(
                LayerPolicyRecord(
                    id=f"{source}_to_{target}",
                    source_layer=source,
                    target_layer=target,
                    status=status,
                    edge_count=len(matching),
                    evidence=evidence,
                    recommended_action=action,
                )
            )
    return records


def find_import_cycles(edges: list[ImportEdgeRecord]) -> list[list[str]]:
    """Return simple internal import cycles from an edge list."""
    adjacency: dict[str, set[str]] = {}
    for edge in edges:
        adjacency.setdefault(edge.source_module, set()).add(edge.target_module)
        adjacency.setdefault(edge.target_module, set())
    cycles: set[tuple[str, ...]] = set()
    for start in sorted(adjacency):
        _visit_cycles(start, start, adjacency, [], cycles)
    return [list(cycle) for cycle in sorted(cycles)]


def write_architecture_report(
    report: ArchitectureReport,
    *,
    output_dir: Path,
) -> tuple[Path, Path, Path, Path, Path]:
    """Write architecture report artefacts."""
    output_dir.mkdir(parents=True, exist_ok=True)
    edge_rows = [record.as_row() for record in report.edges]
    policy_rows = [record.as_row() for record in report.layer_policies]
    cycle_rows = [
        {"cycle_id": f"cycle_{index:03d}", "module_path": " -> ".join(cycle), "length": len(cycle)}
        for index, cycle in enumerate(report.cycles, start=1)
    ]
    edge_jsonl = write_jsonl(edge_rows, output_dir / "import_edges.jsonl")
    edge_csv = write_csv(edge_rows, output_dir / "import_edges.csv")
    policy_jsonl = write_jsonl(policy_rows, output_dir / "layer_policy.jsonl")
    policy_csv = write_csv(policy_rows, output_dir / "layer_policy.csv")
    write_jsonl(cycle_rows, output_dir / "import_cycles.jsonl")
    write_csv(cycle_rows, output_dir / "import_cycles.csv")
    summary_path = output_dir / "summary.json"
    summary_path.write_text(
        json.dumps(report.summary.as_row(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return edge_jsonl, edge_csv, policy_jsonl, policy_csv, summary_path


def _edge(
    source_module: str,
    target_module: str,
    import_kind: ImportKind,
    line: int,
) -> ImportEdgeRecord:
    source_layer = layer_for_module(source_module)
    target_layer = layer_for_module(target_module)
    allowed = _is_allowed_layer_dependency(source_layer, target_layer)
    reason = (
        "Layer dependency respects inward/downward architecture."
        if allowed
        else "Lower architectural layer imports a higher layer."
    )
    if "unknown" in {source_layer, target_layer}:
        allowed = False
        reason = "At least one module is not assigned to a named architecture layer."
    return ImportEdgeRecord(
        source_module=source_module,
        target_module=target_module,
        source_layer=source_layer,
        target_layer=target_layer,
        import_kind=import_kind,
        line=line,
        allowed=allowed,
        reason=reason,
    )


def _normalise_internal_target(module: str) -> str | None:
    if module == "reimburse_atlas" or module.startswith("reimburse_atlas."):
        return module
    return None


def _resolve_import_from(current_module: str, node: ast.ImportFrom) -> str | None:
    if node.level == 0:
        return _normalise_internal_target(node.module or "")
    parts = current_module.split(".")
    package_parts = parts[:-1]
    if node.level > len(package_parts):
        return None
    base_parts = package_parts[: len(package_parts) - node.level + 1]
    if node.module:
        base_parts.extend(node.module.split("."))
    target = ".".join(base_parts)
    return _normalise_internal_target(target)


def _is_allowed_layer_dependency(
    source_layer: ArchitectureLayer,
    target_layer: ArchitectureLayer,
) -> bool:
    if "unknown" in {source_layer, target_layer}:
        return False
    return _LAYER_ORDER[source_layer] >= _LAYER_ORDER[target_layer]


def _internal_modules(root: Path) -> set[str]:
    src_root = root / "src"
    package_root = src_root / "reimburse_atlas"
    return {module_name_for_path(path, src_root) for path in package_root.rglob("*.py")}


def _deduplicate_edges(edges: list[ImportEdgeRecord]) -> list[ImportEdgeRecord]:
    seen: set[tuple[str, str, ImportKind, int]] = set()
    output: list[ImportEdgeRecord] = []
    for edge in edges:
        key = (edge.source_module, edge.target_module, edge.import_kind, edge.line)
        if key in seen:
            continue
        seen.add(key)
        output.append(edge)
    return output


def _visit_cycles(
    start: str,
    current: str,
    adjacency: dict[str, set[str]],
    path: list[str],
    cycles: set[tuple[str, ...]],
) -> None:
    if current in path:
        return
    next_path = [*path, current]
    for neighbour in sorted(adjacency.get(current, set())):
        if neighbour == start and len(next_path) > 1:
            cycles.add(_canonical_cycle([*next_path, start]))
        elif neighbour >= start:
            _visit_cycles(start, neighbour, adjacency, next_path, cycles)


def _canonical_cycle(cycle: list[str]) -> tuple[str, ...]:
    body = cycle[:-1]
    rotations = [tuple(body[index:] + body[:index]) for index in range(len(body))]
    canonical = min(rotations)
    return (*canonical, canonical[0])
