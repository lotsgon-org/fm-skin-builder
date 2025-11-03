from __future__ import annotations
from pathlib import Path
from ...core.css_patcher import run_patch


def run(args) -> None:
    css_dir = Path(args.css)
    out_dir = Path(args.out)
    bundle = Path(args.bundle) if args.bundle else None
    run_patch(
        css_dir=css_dir,
        out_dir=out_dir,
        bundle=bundle,
        patch_direct=args.patch_direct,
        debug_export=args.debug_export,
        backup=args.backup,
    )
