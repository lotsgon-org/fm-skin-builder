from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

DEFAULT_TEXTURE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".svg"}

__all__ = [
    "collect_replacement_stems",
    "load_texture_name_map",
]


def collect_replacement_stems(root: Path, *, extensions: Optional[Iterable[str]] = None) -> List[str]:
    """Return filename stems for replacement assets under *root*."""
    exts = {e.lower() for e in (extensions or DEFAULT_TEXTURE_EXTENSIONS)}
    stems: List[str] = []
    if not root.exists():
        return stems
    for path in root.glob("*.*"):
        if path.suffix.lower() in exts:
            stems.append(path.stem)
    return stems


def load_texture_name_map(skin_root: Path) -> Dict[str, str]:
    """Load mapping.json files that map replacement stems to target texture names."""
    name_map: Dict[str, str] = {}

    def _load_json(path: Path) -> None:
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(key, str) and isinstance(value, str):
                    name_map[key] = value

    assets_dir = skin_root / "assets"
    for fname in ("mapping.json", "map.json"):
        _load_json(assets_dir / fname)
    for subdir in ("icons", "backgrounds"):
        sub_assets = assets_dir / subdir
        for fname in ("mapping.json", "map.json"):
            _load_json(sub_assets / fname)

    return name_map
