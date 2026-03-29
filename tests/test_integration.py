"""Integration tests using real fixture projects."""
from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from reqscan.cli import main
from reqscan.core import run_check


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def test_clean_project_no_issues(fixtures_dir: Path):
    result = run_check(fixtures_dir / "simple_project")
    assert not result.has_issues
    assert result.scanned_files >= 1


def test_unused_dep_detected(fixtures_dir: Path):
    result = run_check(fixtures_dir / "unused_dep")
    assert "boto3" in result.unused_deps
    assert not result.undeclared_imports


def test_undeclared_import_detected(fixtures_dir: Path):
    result = run_check(fixtures_dir / "undeclared_import")
    assert "httpx" in result.undeclared_imports
    assert not result.unused_deps


def test_mismatch_names_no_false_positives(fixtures_dir: Path):
    """import PIL should resolve to Pillow; import yaml should resolve to PyYAML."""
    result = run_check(fixtures_dir / "mismatch_names")
    # No false positives — Pillow and PyYAML should be recognized
    assert "pillow" not in result.undeclared_imports
    assert "pyyaml" not in result.undeclared_imports


def test_pyproject_toml_sources(fixtures_dir: Path):
    result = run_check(fixtures_dir / "pyproject_project")
    assert any("pyproject.toml" in s for s in result.requirements_sources)
    assert not result.has_issues


def test_stdlib_imports_not_flagged(fixtures_dir: Path):
    result = run_check(fixtures_dir / "stdlib_not_flagged")
    undeclared = result.undeclared_imports
    for stdlib_mod in ["os", "sys", "json", "pathlib"]:
        assert stdlib_mod not in undeclared


def test_cli_exit_zero_on_clean(fixtures_dir: Path):
    runner = CliRunner()
    result = runner.invoke(main, [str(fixtures_dir / "simple_project")])
    assert result.exit_code == 0


def test_cli_exit_one_on_issues(fixtures_dir: Path):
    runner = CliRunner()
    result = runner.invoke(main, [str(fixtures_dir / "unused_dep")])
    assert result.exit_code == 1


def test_cli_json_output(fixtures_dir: Path):
    import json

    runner = CliRunner()
    result = runner.invoke(main, [str(fixtures_dir / "unused_dep"), "--json"])
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert "unused_deps" in data
    assert "undeclared_imports" in data
    assert "boto3" in data["unused_deps"]


def test_cli_ignore_package(fixtures_dir: Path):
    runner = CliRunner()
    result = runner.invoke(
        main, [str(fixtures_dir / "unused_dep"), "--ignore-package", "boto3"]
    )
    assert result.exit_code == 0


def test_cli_no_color_flag(fixtures_dir: Path):
    runner = CliRunner()
    result = runner.invoke(main, [str(fixtures_dir / "simple_project"), "--no-color"])
    assert result.exit_code == 0


def test_cli_version():
    from reqscan import __version__

    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert __version__ in result.output
    assert result.exit_code == 0
