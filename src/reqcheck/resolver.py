from __future__ import annotations

from pathlib import Path

from reqcheck.requirements_parser import normalize_package_name

try:
    from importlib.metadata import packages_distributions  # type: ignore[attr-defined]
except ImportError:
    packages_distributions = None

# Well-known import-name → package-name mismatches.
# These are used as a fallback when the package isn't installed in the current env.
KNOWN_MAPPINGS: dict[str, str] = {
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "dotenv": "python-dotenv",
    "dateutil": "python-dateutil",
    "Crypto": "pycryptodome",
    "serial": "pyserial",
    "usb": "pyusb",
    "magic": "python-magic",
    "attr": "attrs",
    "MySQLdb": "mysqlclient",
    "psycopg2": "psycopg2-binary",
    "gi": "PyGObject",
    "wx": "wxPython",
    "pkg_resources": "setuptools",
    "google": "google-cloud",
    "jwt": "PyJWT",
    "nacl": "PyNaCl",
    "OpenSSL": "pyOpenSSL",
    "pydantic": "pydantic",
    "aiohttp": "aiohttp",
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "sqlalchemy": "sqlalchemy",
    "celery": "celery",
    "redis": "redis",
    "boto3": "boto3",
    "botocore": "botocore",
    "paramiko": "paramiko",
    "cryptography": "cryptography",
    "httpx": "httpx",
    "anyio": "anyio",
    "uvicorn": "uvicorn",
    "starlette": "starlette",
    "typer": "typer",
    "rich": "rich",
    "click": "click",
    "pytest": "pytest",
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "scipy": "scipy",
    "torch": "torch",
    "tensorflow": "tensorflow",
    "transformers": "transformers",
}


class ImportPackageResolver:
    """Resolves import names to package names and vice versa."""

    def __init__(self) -> None:
        # normalized_package_name -> set of import names
        self._pkg_to_imports: dict[str, set[str]] = {}
        # import_name -> normalized package name
        self._import_to_pkg: dict[str, str] = {}
        self._build_maps()

    def _build_maps(self) -> None:
        # Layer 1: static known mappings (lowest priority)
        for import_name, pkg_name in KNOWN_MAPPINGS.items():
            norm = normalize_package_name(pkg_name)
            self._import_to_pkg[import_name] = norm
            self._pkg_to_imports.setdefault(norm, set()).add(import_name)

        # Layer 2: live environment data (highest priority, overrides static)
        if packages_distributions is not None:
            try:
                for import_name, dist_names in packages_distributions().items():
                    for dist_name in dist_names:
                        norm = normalize_package_name(dist_name)
                        self._import_to_pkg[import_name] = norm
                        self._pkg_to_imports.setdefault(norm, set()).add(import_name)
            except Exception:
                pass  # degrade to static map only

    def import_to_package(self, import_name: str) -> str | None:
        """Return the normalized package name for an import name, or None if unknown."""
        if import_name in self._import_to_pkg:
            return self._import_to_pkg[import_name]
        # Heuristic: try treating the import name as the package name
        # (e.g. "requests" → "requests", "my_package" → "my-package")
        heuristic = normalize_package_name(import_name.replace("_", "-"))
        return heuristic

    def package_to_imports(self, package_name: str) -> set[str]:
        """Return all known import names for a package name."""
        norm = normalize_package_name(package_name)
        if norm in self._pkg_to_imports:
            return self._pkg_to_imports[norm]
        # Heuristic fallback: the package name itself is likely the import name
        return {norm.replace("-", "_"), norm}

    def is_first_party(self, import_name: str, project_root: Path) -> bool:
        """Return True if import_name appears to be a local module in this project."""
        for candidate in [
            project_root / import_name,
            project_root / f"{import_name}.py",
            project_root / "src" / import_name,
            project_root / "src" / f"{import_name}.py",
        ]:
            if candidate.exists():
                return True
        return False
