"""Contract checks for harness marketplace catalogs and vendor plugin manifests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_MANIFEST = ROOT / ".plugin" / "plugin.json"
CLAUDE_DIR = ROOT / ".claude-plugin"
CURSOR_DIR = ROOT / ".cursor-plugin"
COMPONENT_PATH_FIELDS = (
    "rules",
    "skills",
    "agents",
    "hooks",
    "mcpServers",
    "lspServers",
)
CURSOR_ENTRY_KEYS = frozenset({"name", "source", "description"})
VENDOR_MANIFEST_NAMES = frozenset({"marketplace.json", "plugin.json"})
MARKETPLACE_NAME = "open-plugins-surface-test"
PLUGIN_NAME = "open-plugins-conformance"
PROBE_PATHS = (
    ROOT / "rules",
    ROOT / "skills",
    ROOT / "agents",
    ROOT / "hooks" / "hooks.json",
)


def _load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_claude_catalog_shape() -> None:
    """Claude marketplace.json lists this repo's plugin with source ./."""
    path = CLAUDE_DIR / "marketplace.json"
    assert path.is_file()
    data = _load(path)
    assert isinstance(data, dict)
    assert data["name"] == MARKETPLACE_NAME
    owner = data["owner"]
    assert isinstance(owner, dict)
    assert isinstance(owner["name"], str) and owner["name"]
    plugins = data["plugins"]
    assert isinstance(plugins, list)
    assert len(plugins) == 1
    entry = plugins[0]
    assert entry["name"] == PLUGIN_NAME
    assert entry["source"] == "./"


def test_cursor_catalog_shape() -> None:
    """Cursor marketplace.json lists the same plugin with source . and a tight entry key set."""
    path = CURSOR_DIR / "marketplace.json"
    assert path.is_file()
    data = _load(path)
    assert isinstance(data, dict)
    assert data["name"] == MARKETPLACE_NAME
    owner = data["owner"]
    assert isinstance(owner, dict)
    assert isinstance(owner["name"], str) and owner["name"]
    plugins = data["plugins"]
    assert isinstance(plugins, list)
    assert len(plugins) == 1
    entry = plugins[0]
    assert entry["name"] == PLUGIN_NAME
    assert entry["source"] == "."
    assert set(entry) <= CURSOR_ENTRY_KEYS


def test_source_resolves_to_repo_root_plugin() -> None:
    """Catalog sources resolve to this repo's .plugin/plugin.json."""
    claude = _load(CLAUDE_DIR / "marketplace.json")
    cursor = _load(CURSOR_DIR / "marketplace.json")
    assert isinstance(claude, dict) and isinstance(cursor, dict)
    claude_src = (ROOT / claude["plugins"][0]["source"]).resolve()
    cursor_src = (ROOT / cursor["plugins"][0]["source"]).resolve()
    assert claude_src == ROOT
    assert cursor_src == ROOT
    data = _load(PLUGIN_MANIFEST)
    assert isinstance(data, dict)
    assert data["name"] == PLUGIN_NAME
    for field in COMPONENT_PATH_FIELDS:
        value = data[field]
        assert isinstance(value, str)
        assert value.startswith("./")


def test_claude_vendor_manifest_only() -> None:
    """Claude vendor dir holds marketplace.json and plugin.json only."""
    assert CLAUDE_DIR.is_dir()
    names = {p.name for p in CLAUDE_DIR.iterdir()}
    assert names == VENDOR_MANIFEST_NAMES
    data = _load(CLAUDE_DIR / "plugin.json")
    assert isinstance(data, dict)
    assert data["name"] == PLUGIN_NAME


def test_cursor_vendor_manifest_only() -> None:
    """Cursor vendor dir holds marketplace.json and plugin.json only."""
    assert CURSOR_DIR.is_dir()
    names = {p.name for p in CURSOR_DIR.iterdir()}
    assert names == VENDOR_MANIFEST_NAMES
    data = _load(CURSOR_DIR / "plugin.json")
    assert isinstance(data, dict)
    assert data["name"] == PLUGIN_NAME


def test_probe_tree_unmoved() -> None:
    """Probe surfaces stay at repo root, not under a plugins/ subdirectory."""
    for path in PROBE_PATHS:
        assert path.exists(), f"missing probe path {path}"
    relocated = ROOT / "plugins" / PLUGIN_NAME
    assert not relocated.exists()
