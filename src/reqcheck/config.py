from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from reqcheck.models import ReqcheckConfig

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def _find_config_file(start: Path) -> Path | None:
    """Walk up from start directory looking for pyproject.toml or .reqcheck.toml."""
    current = start.resolve()
    while True:
        for name in (".reqcheck.toml", "pyproject.toml"):
            candidate = current / name
            if candidate.exists():
                return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_config(start: Path, config_file: Path | None = None) -> ReqcheckConfig:
    """Load ReqcheckConfig from a config file, falling back to defaults."""
    cfg_file = config_file or _find_config_file(start)
    if cfg_file is None:
        return ReqcheckConfig()

    try:
        data = tomllib.loads(cfg_file.read_text(encoding="utf-8"))
    except Exception:
        return ReqcheckConfig()

    # Support both [tool.reqcheck] (in pyproject.toml) and top-level [reqcheck] (.reqcheck.toml)
    section: dict[str, Any] = (
        data.get("tool", {}).get("reqcheck", {})
        or data.get("reqcheck", {})
    )

    return ReqcheckConfig(
        ignore_packages=section.get("ignore_packages", []),
        ignore_imports=section.get("ignore_imports", []),
        exclude_dirs=section.get(
            "exclude_dirs", [".venv", "venv", ".git", "__pycache__", "dist", "build"]
        ),
        requirements_files=section.get("requirements_files", []),
        include_dev=section.get("include_dev", False),
    )
