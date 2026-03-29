from pathlib import Path

from reqscan.models import ReqcheckConfig
from reqscan.scanner import find_python_files


def test_finds_python_files(tmp_path: Path):
    (tmp_path / "main.py").write_text("")
    (tmp_path / "utils.py").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    names = {f.name for f in result}
    assert names == {"main.py", "utils.py"}


def test_excludes_venv(tmp_path: Path):
    (tmp_path / "main.py").write_text("")
    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "lib.py").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    names = {f.name for f in result}
    assert "lib.py" not in names


def test_excludes_pycache(tmp_path: Path):
    (tmp_path / "main.py").write_text("")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "main.cpython-311.pyc").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    paths = [str(f) for f in result]
    assert not any("__pycache__" in p for p in paths)


def test_excludes_egg_info(tmp_path: Path):
    (tmp_path / "main.py").write_text("")
    egg = tmp_path / "mypackage.egg-info"
    egg.mkdir()
    (egg / "PKG-INFO").write_text("")
    (egg / "top_level.py").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    names = {f.name for f in result}
    assert "top_level.py" not in names


def test_recursive_scan(tmp_path: Path):
    sub = tmp_path / "subdir"
    sub.mkdir()
    (tmp_path / "main.py").write_text("")
    (sub / "helper.py").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    names = {f.name for f in result}
    assert {"main.py", "helper.py"} == names


def test_ignores_non_py_files(tmp_path: Path):
    (tmp_path / "main.py").write_text("")
    (tmp_path / "README.md").write_text("")
    (tmp_path / "data.json").write_text("")
    config = ReqcheckConfig()
    result = find_python_files(tmp_path, config)
    assert all(f.suffix == ".py" for f in result)
