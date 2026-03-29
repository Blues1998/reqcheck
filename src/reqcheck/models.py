from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScanResult:
    unused_deps: list[str]
    undeclared_imports: list[str]
    scanned_files: int
    requirements_sources: list[str]

    @property
    def has_issues(self) -> bool:
        return bool(self.unused_deps or self.undeclared_imports)

    @property
    def issue_count(self) -> int:
        return len(self.unused_deps) + len(self.undeclared_imports)


@dataclass
class ReqcheckConfig:
    paths: list[str] = field(default_factory=list)
    ignore_packages: list[str] = field(default_factory=list)
    ignore_imports: list[str] = field(default_factory=list)
    exclude_dirs: list[str] = field(
        default_factory=lambda: [".venv", "venv", ".git", "__pycache__", "dist", "build"]
    )
    requirements_files: list[str] = field(default_factory=list)
    include_dev: bool = False
