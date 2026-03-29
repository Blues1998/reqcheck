# reqcheck

> Detect unused and undeclared Python dependencies.

[![CI](https://github.com/blues1998/reqcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/blues1998/reqcheck/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/reqcheck)](https://pypi.org/project/reqcheck)
[![Python](https://img.shields.io/pypi/pyversions/reqcheck)](https://pypi.org/project/reqcheck)

`reqcheck` scans your Python project and reports:

- **Unused dependencies** — packages listed in your requirements that are never imported
- **Undeclared imports** — packages imported in your code that are missing from requirements

## Installation

```bash
pip install reqcheck
```

## Usage

```bash
# Scan the current directory
reqcheck .

# Scan a specific project
reqcheck /path/to/project

# Point to a specific requirements file
reqcheck . --requirements requirements/prod.txt

# Include dev dependencies
reqcheck . --include-dev

# Suppress specific packages from the unused report
reqcheck . --ignore-package boto3

# Output as JSON (useful for CI tooling)
reqcheck . --json
```

### Example output

```
Scanning: /my/project/**/*.py
Scanned 12 file(s) using 1 requirements source(s)

Unused dependencies (listed in requirements but never imported):
  • boto3

Undeclared imports (imported in code but not in requirements):
  • httpx

✗ Found 2 issues
```

Exit codes: `0` = clean, `1` = issues found, `2` = scan error.

## Supported requirements formats

| Format | Support |
|---|---|
| `requirements.txt` | ✓ Full (including `-r` includes) |
| `pyproject.toml` | ✓ PEP 621 `[project.dependencies]` + Poetry |
| `setup.cfg` | ✓ `[options] install_requires` |

## Configuration

Add a `[tool.reqcheck]` section to your `pyproject.toml`:

```toml
[tool.reqcheck]
exclude_dirs = [".venv", "venv", "docs"]
ignore_packages = ["boto3"]        # treat as always-used
ignore_imports = ["mypy_extensions"]  # ignore in undeclared report
include_dev = false
```

## Use as a library

```python
from reqcheck import run_check

result = run_check(".")
print(result.unused_deps)       # ["boto3"]
print(result.undeclared_imports)  # ["httpx"]
print(result.has_issues)          # True
```

## Known limitations

- **Dynamic imports** (`importlib.import_module("name")`) are not detected — only static `import` statements are analyzed.
- **`setup.py`** (legacy format) is not supported; use `pyproject.toml` or `setup.cfg` instead.
- Packages not installed in the current environment are resolved using a static mapping table. If a package is missing from the table, `reqcheck` falls back to treating the import name as the package name.

## Contributing

Contributions welcome! Please open an issue or pull request on [GitHub](https://github.com/blues1998/reqcheck).

## License

MIT
