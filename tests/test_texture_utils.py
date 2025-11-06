from pathlib import Path

from src.core.texture_utils import collect_replacement_stems, load_texture_name_map


def test_collect_replacement_stems_filters_extensions(tmp_path: Path):
    icons = tmp_path / "assets" / "icons"
    icons.mkdir(parents=True)
    (icons / "one.png").write_bytes(b"")
    (icons / "two.JPG").write_bytes(b"")
    (icons / "three.svg").write_bytes(b"")
    (icons / "ignore.txt").write_bytes(b"")

    stems = collect_replacement_stems(icons)

    assert sorted(stems) == ["one", "three", "two"]


def test_load_texture_name_map_reads_overrides(tmp_path: Path):
    assets = tmp_path / "assets"
    assets.mkdir(parents=True)
    (assets / "mapping.json").write_text('{"src": "dest"}', encoding="utf-8")
    icons = assets / "icons"
    icons.mkdir(parents=True)
    (icons / "map.json").write_text('{"icon": "IconTarget"}', encoding="utf-8")

    mapping = load_texture_name_map(tmp_path)

    assert mapping["src"] == "dest"
    assert mapping["icon"] == "IconTarget"
