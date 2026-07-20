# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
"""Unit tests for uv detection helpers in the extensions package."""

import pytest

from rockcraft.errors import ExtensionError
from rockcraft.extensions._python_utils import uses_uv, validate_uv_lockfile


def test_uses_uv_true_when_both_files_present(tmp_path):
    (tmp_path / "uv.lock").write_text("")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    assert uses_uv(tmp_path) is True


def test_uses_uv_false_when_only_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    assert uses_uv(tmp_path) is False


def test_uses_uv_false_when_only_uv_lock(tmp_path):
    (tmp_path / "uv.lock").write_text("")
    assert uses_uv(tmp_path) is False


def test_uses_uv_false_when_neither(tmp_path):
    assert uses_uv(tmp_path) is False


def test_validate_uv_lockfile_ok_when_both_present(tmp_path):
    (tmp_path / "uv.lock").write_text("")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    # Should not raise.
    validate_uv_lockfile(tmp_path)


def test_validate_uv_lockfile_ok_when_neither_present(tmp_path):
    # Not a uv project at all; should not raise.
    validate_uv_lockfile(tmp_path)


def test_validate_uv_lockfile_ok_when_only_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n")
    # pip project; should not raise.
    validate_uv_lockfile(tmp_path)


def test_validate_uv_lockfile_raises_when_lock_without_pyproject(tmp_path):
    (tmp_path / "uv.lock").write_text("")
    with pytest.raises(ExtensionError) as exc:
        validate_uv_lockfile(tmp_path)
    assert "both uv.lock and pyproject.toml" in str(exc.value)
