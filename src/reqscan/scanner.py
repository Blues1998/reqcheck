from __future__ import annotations

import os
from pathlib import Path

from reqscan.models import ReqcheckConfig


def find_python_files(root: Path, config: ReqcheckConfig) -> list[Path]:
    """Recursively find all .py files under root, respecting excluded directories."""
    exclude_dirs = set(config.exclude_dirs)
    result: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories from traversal (mutate in-place)
        dirnames[:] = [
            d
            for d in dirnames
            if d not in exclude_dirs and not d.endswith(".egg-info")
        ]
        for fname in filenames:
            if fname.endswith(".py"):
                result.append(Path(dirpath) / fname)

    return result
