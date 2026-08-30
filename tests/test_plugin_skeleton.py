"""Contract checks for the plugin skeleton (manifest + gitignore)."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COMPONENT_PATH_FIELDS = (
    "rules",
    "skills",
    "agents",
    "hooks",
    "mcpServers",
    "lspServers",
)


def test_plugin_manifest_name_and_component_paths() -> None:
    data = json.loads((ROOT / ".plugin" / "plugin.json").read_text(encoding="utf-8"))
    name = data["name"]

    assert isinstance(name, str)
    assert 1 <= len(name) <= 64
    assert re.fullmatch(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?", name)
    assert "--" not in name and ".." not in name

    for field in COMPONENT_PATH_FIELDS:
        value = data[field]
        assert isinstance(value, str)
        assert value.startswith("./")


def test_gitignore_ignores_work_directory() -> None:
    lines = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    assert "work/" in lines
    assert "plugintest/" in lines
    assert ".conformance-work" in lines
