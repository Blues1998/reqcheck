from __future__ import annotations

from pathlib import Path

from reqscan.config import load_config
from reqscan.import_parser import extract_imports_from_file
from reqscan.models import ReqcheckConfig, ScanResult
from reqscan.requirements_parser import (
    discover_and_parse,
    normalize_package_name,
    parse_requirements_txt,
)
from reqscan.resolver import ImportPackageResolver
from reqscan.scanner import find_python_files
from reqscan.stdlib_filter import is_stdlib_module


def run_check(
    path: str | Path = ".",
    config: ReqcheckConfig | None = None,
    *,
    requirements_files: list[str] | None = None,
    ignore_packages: list[str] | None = None,
    ignore_imports: list[str] | None = None,
    include_dev: bool = False,
) -> ScanResult:
    """Scan a Python project and return a ScanResult describing dependency issues.

    Args:
        path: Root directory of the project to scan.
        config: Optional pre-built config. If None, auto-loaded from config files.
        requirements_files: Override requirements file paths (relative or absolute).
        ignore_packages: Additional packages to treat as always-used.
        ignore_imports: Additional import names to ignore in the undeclared report.
        include_dev: Include dev/optional dependencies.
    """
    root = Path(path).resolve()

    # Load base config then apply overrides
    if config is None:
        config = load_config(root)

    if requirements_files:
        config.requirements_files = requirements_files
    if ignore_packages:
        config.ignore_packages = list(set(config.ignore_packages) | set(ignore_packages))
    if ignore_imports:
        config.ignore_imports = list(set(config.ignore_imports) | set(ignore_imports))
    if include_dev:
        config.include_dev = True

    # --- Step 1: Parse requirements ---
    if config.requirements_files:
        declared_packages: set[str] = set()
        sources: list[str] = []
        for rf in config.requirements_files:
            fpath = Path(rf) if Path(rf).is_absolute() else root / rf
            pkgs = parse_requirements_txt(fpath)
            declared_packages |= pkgs
            if pkgs:
                sources.append(str(fpath))
    else:
        declared_packages, sources = discover_and_parse(root, include_dev=config.include_dev)

    # Normalize ignore lists
    ignored_packages = {normalize_package_name(p) for p in config.ignore_packages}
    ignored_imports = set(config.ignore_imports)

    # --- Step 2: Find and parse Python files ---
    py_files = find_python_files(root, config)

    raw_imports: set[str] = set()
    for f in py_files:
        raw_imports |= extract_imports_from_file(f)

    # --- Step 3: Filter imports ---
    resolver = ImportPackageResolver()
    external_imports: set[str] = set()
    for imp in raw_imports:
        if imp in ignored_imports:
            continue
        if is_stdlib_module(imp):
            continue
        if resolver.is_first_party(imp, root):
            continue
        external_imports.add(imp)

    # --- Step 4: Resolve import names → package names ---
    imported_packages: set[str] = set()
    for imp in external_imports:
        pkg = resolver.import_to_package(imp)
        if pkg:
            imported_packages.add(pkg)

    # --- Step 5: Compute unused and undeclared ---
    unused = sorted(declared_packages - imported_packages - ignored_packages)
    undeclared = sorted(imported_packages - declared_packages)

    return ScanResult(
        unused_deps=unused,
        undeclared_imports=undeclared,
        scanned_files=len(py_files),
        requirements_sources=sources,
    )
