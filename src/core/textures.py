from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os

import UnityPy

from .logger import get_logger

log = get_logger(__name__)


def _collect_image_bytes(root: Path) -> Dict[str, bytes]:
    """Collect replacement images under a root folder (e.g., assets/icons or assets/backgrounds).

    Returns map of asset_name (filename without extension) -> bytes.
    The name includes any variant suffix (e.g., Icon_x2) so exact matches work.
    """
    replacements: Dict[str, bytes] = {}
    if not root.exists():
        return replacements
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            continue
        name = p.stem  # include suffixes like _x2 in the name
        try:
            replacements[name] = p.read_bytes()
        except Exception as e:
            log.warning(f"Failed to read image {p}: {e}")
    return replacements


def _swap_textures_in_env(env, replacements: Dict[str, bytes]) -> int:
    """Apply replacements to Texture2D assets in UnityPy env by matching names.

    Returns number of textures replaced.
    """
    if not replacements:
        return 0
    replaced = 0
    for obj in getattr(env, "objects", []):
        if getattr(getattr(obj, "type", None), "name", None) != "Texture2D":
            continue
        try:
            data = obj.read()
        except Exception:
            continue
        name = getattr(data, "m_Name", None) or getattr(data, "name", None)
        if not name:
            continue
        buf = replacements.get(name)
        if buf is None:
            continue
        # Try UnityPy-friendly APIs; fallback to attribute for tests
        try:
            if hasattr(data, "set_image"):
                data.set_image(buf)
            elif hasattr(data, "image_data"):
                data.image_data = buf
            else:
                setattr(data, "_replaced_bytes", buf)  # test fallback
            replaced += 1
            # Persist typetree change if UnityPy supports it
            if hasattr(data, "save"):
                try:
                    data.save()
                except Exception:
                    pass
            log.info(f"  [TEXTURE] Replaced Texture2D '{name}' ({len(buf)} bytes)")
        except Exception as e:
            log.warning(f"  [TEXTURE] Failed to replace texture '{name}': {e}")
    return replaced


def swap_textures(css_dir: Path, bundle_path: Path, out_dir: Path, dry_run: bool = False) -> Optional[Path]:
    """Swap icons/backgrounds found under skin assets into the given bundle.

    Looks under:
      - assets/icons/
      - assets/backgrounds/
    """
    skin_root = css_dir
    icons_dir = skin_root / "assets" / "icons"
    bgs_dir = skin_root / "assets" / "backgrounds"
    repl = {}
    repl.update(_collect_image_bytes(icons_dir))
    repl.update(_collect_image_bytes(bgs_dir))
    if not repl:
        return None

    env = UnityPy.load(str(bundle_path))
    count = _swap_textures_in_env(env, repl)
    if count == 0:
        log.info("No texture replacements applied.")
        return None
    if dry_run:
        log.info(f"[DRY-RUN] Would replace {count} textures in {bundle_path.name}")
        return None
    # Write out modified bundle next to CSS patch outputs
    out_dir.mkdir(parents=True, exist_ok=True)
    name, ext = os.path.splitext(bundle_path.name)
    out_file = out_dir / f"{name}_modified{ext}"
    with open(out_file, "wb") as f:
        f.write(env.file.save())
    log.info(f"💾 Saved texture-swapped bundle → {out_file}")
    return out_file
