"""Contracts for cwd plugintest work-root resolution."""

from __future__ import annotations

import importlib.util
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAMP = re.compile(r"^\d{8}T\d{6}Z$")


def _load():
    spec = importlib.util.spec_from_file_location(
        "work_root", ROOT / "scripts" / "work_root.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_conformance_work_override_skips_plugintest(tmp_path: Path) -> None:
    wr = _load()
    override = tmp_path / "explicit"
    override.mkdir()
    cwd = tmp_path / "launch"
    cwd.mkdir()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    result = wr.resolve_work_dir(
        create=True,
        cwd=cwd,
        plugin_root=plugin,
        env={"CONFORMANCE_WORK": str(override)},
    )
    assert result == override
    assert not (cwd / "plugintest").exists()


def test_ensure_creates_stamp_current_and_pointer(tmp_path: Path) -> None:
    wr = _load()
    cwd = tmp_path / "launch"
    cwd.mkdir()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    result = wr.resolve_work_dir(create=True, cwd=cwd, plugin_root=plugin, env={})
    suite = cwd / "plugintest"
    current = suite / "CURRENT"
    assert result.parent == suite
    assert STAMP.fullmatch(result.name)
    assert current.is_symlink()
    assert os.readlink(current) == result.name
    assert current.resolve() == result.resolve()
    pointer = plugin / ".conformance-work"
    assert pointer.read_text(encoding="utf-8").strip() == str(result.resolve())
    assert not (plugin / "work").exists()


def test_second_ensure_reuses_current(tmp_path: Path) -> None:
    wr = _load()
    cwd = tmp_path / "launch"
    cwd.mkdir()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    first = wr.resolve_work_dir(create=True, cwd=cwd, plugin_root=plugin, env={})
    second = wr.resolve_work_dir(create=True, cwd=cwd, plugin_root=plugin, env={})
    assert second == first
    stamps = [p for p in (cwd / "plugintest").iterdir() if p.name != "CURRENT"]
    assert len(stamps) == 1


def test_pointer_used_when_cwd_differs(tmp_path: Path) -> None:
    wr = _load()
    launch = tmp_path / "launch"
    launch.mkdir()
    plugin = tmp_path / "plugin"
    plugin.mkdir()
    created = wr.resolve_work_dir(create=True, cwd=launch, plugin_root=plugin, env={})
    other = tmp_path / "other"
    other.mkdir()
    found = wr.resolve_work_dir(create=False, cwd=other, plugin_root=plugin, env={})
    assert found == created.resolve()
