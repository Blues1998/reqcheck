import warnings

from reqcheck.import_parser import extract_imports_from_source


def test_simple_import():
    src = "import requests"
    assert extract_imports_from_source(src) == {"requests"}


def test_from_import():
    src = "from flask import Flask"
    assert extract_imports_from_source(src) == {"flask"}


def test_import_submodule_returns_top_level():
    src = "import os.path"
    assert extract_imports_from_source(src) == {"os"}


def test_from_submodule_returns_top_level():
    src = "from urllib.parse import urlencode"
    assert extract_imports_from_source(src) == {"urllib"}


def test_relative_import_excluded():
    src = "from . import utils"
    assert extract_imports_from_source(src) == set()


def test_relative_import_parent_excluded():
    src = "from .. import models"
    assert extract_imports_from_source(src) == set()


def test_multiple_imports():
    src = "import requests\nimport click\nfrom rich import console"
    result = extract_imports_from_source(src)
    assert result == {"requests", "click", "rich"}


def test_import_inside_function():
    src = """
def foo():
    import httpx
    return httpx.get("http://example.com")
"""
    assert "httpx" in extract_imports_from_source(src)


def test_import_in_try_except():
    src = """
try:
    import ujson as json
except ImportError:
    import json
"""
    result = extract_imports_from_source(src)
    assert "ujson" in result
    assert "json" in result


def test_type_checking_import():
    src = """
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pandas as pd
"""
    result = extract_imports_from_source(src)
    assert "pandas" in result


def test_syntax_error_returns_empty():
    src = "def foo(: invalid syntax"
    with warnings.catch_warnings(record=True):
        result = extract_imports_from_source(src, filename="bad.py")
    assert result == set()


def test_alias_import():
    src = "import numpy as np"
    assert extract_imports_from_source(src) == {"numpy"}


def test_star_import():
    src = "from os import *"
    assert extract_imports_from_source(src) == {"os"}
