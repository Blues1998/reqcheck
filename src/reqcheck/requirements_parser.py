from __future__ import annotations

import configparser
import re
import sys
import warnings
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[no-reattr]


def normalize_package_name(name: str) -> str:
    """PEP 503 normalization: collapse [-_.] runs to a single hyphen, lowercase."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _parse_requirement_line(line: str) -> str | None:
    """Parse a single requirement line and return the normalized package name, or None."""
    line = line.strip()
    # Strip inline comment
    comment_idx = line.find(" #")
    if comment_idx != -1:
        line = line[:comment_idx].strip()
    if not line:
        return None
    try:
        req = Requirement(line)
        return normalize_package_name(req.name)
    except InvalidRequirement:
        return None


def parse_requirements_txt(path: Path, seen: set[Path] | None = None) -> set[str]:
    """Parse a requirements.txt file, handling -r includes recursively."""
    if seen is None:
        seen = set()
    resolved = path.resolve()
    if resolved in seen:
        return set()
    seen.add(resolved)

    packages: set[str] = set()
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        warnings.warn(f"Could not read {path}: {exc}", stacklevel=2)
        return packages

    continuation = ""
    for line in lines:
        # Handle line continuation
        if line.endswith("\\"):
            continuation += line[:-1].strip() + " "
            continue
        line = continuation + line
        continuation = ""

        # Strip comments and whitespace
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Handle -r / --requirement includes
        if stripped.startswith("-r ") or stripped.startswith("--requirement "):
            include_path = stripped.split(None, 1)[1].strip()
            include_file = path.parent / include_path
            packages |= parse_requirements_txt(include_file, seen)
            continue

        # Skip other option lines (e.g. -i, --index-url, --extra-index-url, -c, -f, -e)
        if stripped.startswith("-"):
            continue

        pkg = _parse_requirement_line(stripped)
        if pkg:
            packages.add(pkg)

    return packages


def parse_pyproject_toml(path: Path, include_dev: bool = False) -> set[str]:
    """Parse dependencies from a pyproject.toml file (PEP 621 and Poetry)."""
    packages: set[str] = set()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        warnings.warn(f"Could not parse {path}: {exc}", stacklevel=2)
        return packages

    # PEP 621: [project].dependencies
    project = data.get("project", {})
    for dep in project.get("dependencies", []):
        pkg = _parse_requirement_line(dep)
        if pkg:
            packages.add(pkg)

    if include_dev:
        # PEP 621: [project.optional-dependencies]
        for group_deps in project.get("optional-dependencies", {}).values():
            for dep in group_deps:
                pkg = _parse_requirement_line(dep)
                if pkg:
                    packages.add(pkg)

    # Poetry: [tool.poetry.dependencies]
    poetry = data.get("tool", {}).get("poetry", {})
    if poetry:
        for name, val in poetry.get("dependencies", {}).items():
            if name.lower() == "python":
                continue
            packages.add(normalize_package_name(name))
        if include_dev:
            for name in poetry.get("dev-dependencies", {}):
                packages.add(normalize_package_name(name))
            for group in poetry.get("group", {}).values():
                for name in group.get("dependencies", {}):
                    packages.add(normalize_package_name(name))

    return packages


def parse_setup_cfg(path: Path, include_dev: bool = False) -> set[str]:
    """Parse install_requires (and optionally extras_require) from setup.cfg."""
    packages: set[str] = set()
    cfg = configparser.ConfigParser()
    try:
        cfg.read(path, encoding="utf-8")
    except Exception as exc:
        warnings.warn(f"Could not parse {path}: {exc}", stacklevel=2)
        return packages

    for line in cfg.get("options", "install_requires", fallback="").splitlines():
        pkg = _parse_requirement_line(line)
        if pkg:
            packages.add(pkg)

    if include_dev:
        extras_raw = cfg.get("options.extras_require", "dev", fallback="")
        for line in extras_raw.splitlines():
            pkg = _parse_requirement_line(line)
            if pkg:
                packages.add(pkg)

    return packages


def discover_and_parse(root: Path, include_dev: bool = False) -> tuple[set[str], list[str]]:
    """Auto-discover requirements files under root and parse them all.

    Returns (packages, sources) where sources is a list of file paths found.
    """
    packages: set[str] = set()
    sources: list[str] = []

    candidates = [
        ("requirements.txt", parse_requirements_txt),
        ("requirements-dev.txt", parse_requirements_txt) if include_dev else None,
        ("requirements/base.txt", parse_requirements_txt),
        ("requirements/prod.txt", parse_requirements_txt),
    ]
    if include_dev:
        candidates += [
            ("requirements/dev.txt", parse_requirements_txt),
            ("requirements/test.txt", parse_requirements_txt),
        ]

    for entry in candidates:
        if entry is None:
            continue
        fname, parser = entry
        fpath = root / fname
        if fpath.exists():
            pkgs = parser(fpath)
            if pkgs:
                packages |= pkgs
                sources.append(str(fpath))

    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        pkgs = parse_pyproject_toml(pyproject, include_dev=include_dev)
        if pkgs:
            packages |= pkgs
            sources.append(str(pyproject))

    setup_cfg = root / "setup.cfg"
    if setup_cfg.exists():
        pkgs = parse_setup_cfg(setup_cfg, include_dev=include_dev)
        if pkgs:
            packages |= pkgs
            sources.append(str(setup_cfg))

    return packages, sources
