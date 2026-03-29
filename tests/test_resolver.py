from unittest.mock import patch

from reqdiff.resolver import ImportPackageResolver


def test_known_mapping_pil():
    resolver = ImportPackageResolver()
    result = resolver.import_to_package("PIL")
    assert result == "pillow"


def test_known_mapping_yaml():
    resolver = ImportPackageResolver()
    result = resolver.import_to_package("yaml")
    assert result == "pyyaml"


def test_known_mapping_sklearn():
    resolver = ImportPackageResolver()
    result = resolver.import_to_package("sklearn")
    assert result == "scikit-learn"


def test_heuristic_fallback():
    resolver = ImportPackageResolver()
    # "requests" is not in KNOWN_MAPPINGS but is a common package
    result = resolver.import_to_package("requests")
    assert result == "requests"


def test_heuristic_underscore_to_hyphen():
    resolver = ImportPackageResolver()
    result = resolver.import_to_package("my_package")
    assert result == "my-package"


def test_package_to_imports_known():
    resolver = ImportPackageResolver()
    imports = resolver.package_to_imports("Pillow")
    assert "PIL" in imports


def test_package_to_imports_heuristic_fallback():
    resolver = ImportPackageResolver()
    imports = resolver.package_to_imports("some-unknown-pkg")
    assert "some_unknown_pkg" in imports or "some-unknown-pkg" in imports


def test_live_env_data_overrides_static(tmp_path):
    """Live packages_distributions() data should take priority over static mappings."""
    mock_data = {"mockpkg": ["mock-package"]}
    with patch("reqdiff.resolver.packages_distributions", return_value=mock_data):
        resolver = ImportPackageResolver()
    assert resolver.import_to_package("mockpkg") == "mock-package"


def test_is_first_party_finds_local_package(tmp_path):
    (tmp_path / "myapp").mkdir()
    (tmp_path / "myapp" / "__init__.py").write_text("")
    resolver = ImportPackageResolver()
    assert resolver.is_first_party("myapp", tmp_path)


def test_is_first_party_finds_src_layout(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "myapp").mkdir()
    (src / "myapp" / "__init__.py").write_text("")
    resolver = ImportPackageResolver()
    assert resolver.is_first_party("myapp", tmp_path)


def test_is_first_party_false_for_external(tmp_path):
    resolver = ImportPackageResolver()
    assert not resolver.is_first_party("requests", tmp_path)
