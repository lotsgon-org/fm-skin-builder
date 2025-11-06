from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .css_utils import load_css_selector_overrides, load_css_vars
from .logger import get_logger

log = get_logger(__name__)

__all__ = [
    "collect_css_from_dir",
    "load_targeting_hints",
]


def collect_css_from_dir(
    css_dir: Path,
) -> Tuple[Dict[str, str], Dict[Tuple[str, str], str]]:
    """Collect CSS variable and selector overrides from a directory."""
    css_vars: Dict[str, str] = {}
    selector_overrides: Dict[Tuple[str, str], str] = {}

    files: List[Path] = []
    if (css_dir / "config.json").exists():
        colours = css_dir / "colours"
        if colours.exists():
            files.extend(sorted(colours.glob("*.uss")))
            files.extend(sorted(colours.glob("*.css")))
        files.extend(sorted(css_dir.glob("*.uss")))
        files.extend(sorted(css_dir.glob("*.css")))
    else:
        files.extend(sorted(css_dir.glob("*.uss")))
        files.extend(sorted(css_dir.glob("*.css")))

    for css_file in files:
        try:
            css_vars.update(load_css_vars(css_file))
            selector_overrides.update(load_css_selector_overrides(css_file))
        except Exception as exc:
            log.warning("Failed to parse %s: %s", css_file, exc)

    log.info(
        "Total CSS vars: %s, selector overrides: %s from %s files",
        len(css_vars),
        len(selector_overrides),
        len(files),
    )
    return css_vars, selector_overrides


def load_targeting_hints(
    css_dir: Path,
) -> Tuple[
    Optional[Set[str]],
    Optional[Set[str]],
    Optional[Set[Tuple[str, str]]],
]:
    """Load optional targeting hints from a skin or CSS directory."""
    hints_path = css_dir / "hints.txt"
    if not hints_path.exists():
        return None, None, None

    assets: Set[str] = set()
    selectors: Set[str] = set()
    selector_props: Set[Tuple[str, str]] = set()

    try:
        for raw in hints_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            match_asset = re.match(
                r"^asset\s*[:=]\s*(.+)$", line, re.IGNORECASE)
            if match_asset:
                names = [item.strip() for item in re.split(
                    r",|;", match_asset.group(1)) if item.strip()]
                assets.update(names)
                continue
            match_selector = re.match(
                r"^selector\s*[:=]\s*(.+)$", line, re.IGNORECASE)
            if match_selector:
                rest = match_selector.group(1).strip()
                if " " in rest:
                    selector, prop = rest.split(None, 1)
                    selectors.add(selector.strip())
                    selector_props.add((selector.strip(), prop.strip()))
                else:
                    selectors.add(rest)
    except Exception as exc:
        log.warning("Failed to parse targeting hints at %s: %s",
                    hints_path, exc)

    return assets or None, selectors or None, selector_props or None
