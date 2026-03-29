from pathlib import Path

from reqcheck.requirements_parser import (
    normalize_package_name,
    parse_pyproject_toml,
    parse_requirements_txt,
    parse_setup_cfg,
)


def test_normalize_package_name():
    assert normalize_package_name("Pillow") == "pillow"
    assert normalize_package_name("PyYAML") == "pyyaml"
    assert normalize_package_name("python-dotenv") == "python-dotenv"
    assert normalize_package_name("my_package") == "my-package"
    assert normalize_package_name("My.Package") == "my-package"


def test_parse_simple_requirements(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("requests\nclick>=8.0\nrich[all]\n")
    result = parse_requirements_txt(req)
    assert "requests" in result
    assert "click" in result
    assert "rich" in result


def test_parse_requirements_skips_comments(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("# this is a comment\nrequests  # inline comment\n")
    result = parse_requirements_txt(req)
    assert "requests" in result
    assert len(result) == 1


def test_parse_requirements_skips_blank_lines(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("\n\nrequests\n\n")
    result = parse_requirements_txt(req)
    assert result == {"requests"}


def test_parse_requirements_skips_option_lines(tmp_path: Path):
    req = tmp_path / "requirements.txt"
    req.write_text("-i https://pypi.org/simple\n--index-url https://pypi.org\nrequests\n")
    result = parse_requirements_txt(req)
    assert result == {"requests"}


def test_parse_requirements_r_include(tmp_path: Path):
    base = tmp_path / "base.txt"
    base.write_text("requests\n")
    main = tmp_path / "requirements.txt"
    main.write_text("-r base.txt\nclick\n")
    result = parse_requirements_txt(main)
    assert "requests" in result
    assert "click" in result


def test_parse_requirements_r_cycle_safe(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("-r b.txt\nrequests\n")
    b.write_text("-r a.txt\nclick\n")
    result = parse_requirements_txt(a)
    assert "requests" in result
    assert "click" in result


def test_parse_pyproject_pep621(tmp_path: Path):
    ppt = tmp_path / "pyproject.toml"
    ppt.write_text(
        '[project]\ndependencies = ["requests>=2.0", "click"]\n'
    )
    result = parse_pyproject_toml(ppt)
    assert "requests" in result
    assert "click" in result


def test_parse_pyproject_optional_deps_excluded_by_default(tmp_path: Path):
    ppt = tmp_path / "pyproject.toml"
    ppt.write_text(
        '[project]\ndependencies = ["requests"]\n'
        '[project.optional-dependencies]\ndev = ["pytest"]\n'
    )
    result = parse_pyproject_toml(ppt, include_dev=False)
    assert "requests" in result
    assert "pytest" not in result


def test_parse_pyproject_optional_deps_included_with_flag(tmp_path: Path):
    ppt = tmp_path / "pyproject.toml"
    ppt.write_text(
        '[project]\ndependencies = ["requests"]\n'
        '[project.optional-dependencies]\ndev = ["pytest"]\n'
    )
    result = parse_pyproject_toml(ppt, include_dev=True)
    assert "pytest" in result


def test_parse_setup_cfg(tmp_path: Path):
    cfg = tmp_path / "setup.cfg"
    cfg.write_text(
        "[options]\ninstall_requires =\n    requests>=2.0\n    click\n"
    )
    result = parse_setup_cfg(cfg)
    assert "requests" in result
    assert "click" in result
