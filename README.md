# reqdiff

> Detect unused and undeclared Python dependencies.

[![CI](https://github.com/blues1998/reqdiff/actions/workflows/ci.yml/badge.svg)](https://github.com/blues1998/reqdiff/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/reqdiff)](https://pypi.org/project/reqdiff)
[![Python](https://img.shields.io/pypi/pyversions/reqdiff)](https://pypi.org/project/reqdiff)

`reqdiff` scans your Python project and reports:

- **Unused dependencies** — packages listed in your requirements that are never imported
- **Undeclared imports** — packages imported in your code that are missing from requirements

## Installation

```bash
pip install reqdiff
```

## Usage

```bash
# Scan the current directory
reqdiff .

# Scan a specific project
reqdiff /path/to/project

# Point to a specific requirements file
reqdiff . --requirements requirements/prod.txt

# Include dev dependencies
reqdiff . --include-dev

# Suppress specific packages from the unused report
reqdiff . --ignore-package boto3

# Output as JSON (useful for CI tooling)
reqdiff . --json
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

Add a `[tool.reqdiff]` section to your `pyproject.toml`:

```toml
[tool.reqdiff]
exclude_dirs = [".venv", "venv", "docs"]
ignore_packages = ["boto3"]        # treat as always-used
ignore_imports = ["mypy_extensions"]  # ignore in undeclared report
include_dev = false
```

## Use as a library

```python
from reqdiff import run_check

result = run_check(".")
print(result.unused_deps)       # ["boto3"]
print(result.undeclared_imports)  # ["httpx"]
print(result.has_issues)          # True
```

## Known limitations

- **Dynamic imports** (`importlib.import_module("name")`) are not detected — only static `import` statements are analyzed.
- **`setup.py`** (legacy format) is not supported; use `pyproject.toml` or `setup.cfg` instead.
- Packages not installed in the current environment are resolved using a static mapping table. If a package is missing from the table, `reqdiff` falls back to treating the import name as the package name.

## Contributing

Contributions welcome! Please open an issue or pull request on [GitHub](https://github.com/blues1998/reqdiff).

## License

MIT
