from reqscan.stdlib_filter import is_stdlib_module


def test_known_stdlib_modules():
    assert is_stdlib_module("os")
    assert is_stdlib_module("sys")
    assert is_stdlib_module("json")
    assert is_stdlib_module("pathlib")
    assert is_stdlib_module("re")
    assert is_stdlib_module("typing")
    assert is_stdlib_module("collections")
    assert is_stdlib_module("itertools")
    assert is_stdlib_module("functools")
    assert is_stdlib_module("datetime")
    assert is_stdlib_module("io")
    assert is_stdlib_module("abc")
    assert is_stdlib_module("ast")
    assert is_stdlib_module("unittest")


def test_submodule_is_stdlib():
    assert is_stdlib_module("os.path")
    assert is_stdlib_module("collections.abc")
    assert is_stdlib_module("urllib.parse")


def test_known_non_stdlib():
    assert not is_stdlib_module("requests")
    assert not is_stdlib_module("click")
    assert not is_stdlib_module("rich")
    assert not is_stdlib_module("numpy")
    assert not is_stdlib_module("pandas")
    assert not is_stdlib_module("flask")
    assert not is_stdlib_module("django")


def test_builtin_modules():
    assert is_stdlib_module("_thread")
    assert is_stdlib_module("_io")
