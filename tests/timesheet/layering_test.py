"""The contract must not depend on its implementations."""

import ast
from pathlib import Path

from jirahours.timesheet import base


def test_base_does_not_import_from_jirahours() -> None:
    """base.py imports nothing from jirahours, so it cannot pull in an implementation."""
    tree = ast.parse(Path(base.__file__).read_text())
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    assert [name for name in imported if name.startswith("jirahours")] == []
