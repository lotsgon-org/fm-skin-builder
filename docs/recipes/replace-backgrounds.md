# Replace background images (Texture2D)

Replace background textures that appear in panels or screens.

## 1) Opt in via includes

`skins/<skin>/config.json`:

```json
{
  "schema_version": 2,
  "name": "Demo",
  "includes": ["assets/backgrounds"]
}
```

## 2) Place images

- Put files in `skins/<skin>/assets/backgrounds/`
- File name (without extension) must match the Texture2D name in the bundle.
- Supported extensions: `.png`, `.jpg`, `.jpeg`

Examples:
```
assets/backgrounds/
  PanelBg.png
  PanelBg_x2.png
  PanelBg_x4.png
```

You can also use `Name@2x.png`, `Name@4x.png` suffixes. Cross-format replacements (e.g., replacing a PNG-named texture with a JPG file) are allowed; a warning is logged and the replacement still applies.

## 3) Run the patcher

```
python -m src.cli.main patch skins/<skin> --out build
```

- Add `--dry-run` to preview.

## Variant awareness and warnings

- If multiple variants exist in the bundle (1x/2x/4x) but you provide only a subset, the patcher logs a warning and replaces only the provided variants.
- No auto-scaling is performed.

## Troubleshooting

- Use `--debug-export` to export assets and discover the exact Texture2D names.
- If nothing gets written, confirm that the names match and that your config includes the correct feature.
