from __future__ import annotations

import ast
import warnings
from pathlib import Path


def extract_imports_from_source(source: str, filename: str = "<unknown>") -> set[str]:
    """Parse Python source and return a set of top-level external import names.

    Relative imports (from . import x) are excluded.
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as exc:
        warnings.warn(f"Skipping {filename}: syntax error: {exc}", stacklevel=2)
        return set()

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                # "import os.path" → top-level module is "os"
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            # Skip relative imports (level > 0 means from . import or from .. import)
            if node.level == 0 and node.module:
                names.add(node.module.split(".")[0])

    return names


def extract_imports_from_file(path: Path) -> set[str]:
    """Read a .py file and extract top-level import names."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        warnings.warn(f"Skipping {path}: could not read file: {exc}", stacklevel=2)
        return set()
    return extract_imports_from_source(source, filename=str(path))
