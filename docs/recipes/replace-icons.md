# Replace app icons (Texture2D)

This shows how to replace icon textures by name with optional high-DPI variants.

## 1) Opt in via includes

`skins/<skin>/config.json`:

```json
{
  "schema_version": 2,
  "name": "Demo",
  "includes": ["assets/icons"]
}
```

## 2) Place images

- Put files in `skins/<skin>/assets/icons/`
- File name (without extension) must match the Texture2D name in the bundle.
- Supported extensions: `.png`, `.jpg`, `.jpeg`

Examples:
```
assets/icons/
  Search.png          # 1x
  Search_x2.png       # 2x (retina)
  Search_x4.png       # 4x (ultra-high DPI)
```

Also supported: `Name@2x.png`, `Name@4x.png`. Cross-format replacements (e.g., bundle texture named with PNG but you provide JPG) are allowed; the tool logs a warning and proceeds.

## 3) Run the patcher

```
python -m src.cli.main patch skins/<skin> --out build
```

- Use `--dry-run` to preview without writing files.

## Variant awareness and warnings

- If the bundle contains variants for a texture (e.g., `Search`, `Search_x2`, `Search_x4`) and you only provide one of them, you'll get a warning like:
  `Only 1/3 variants provided for 'Search' (provided: [1], missing: [2, 4])`
- The patcher replaces only the provided matching variants and skips missing ones.
- It does not upscale/downscale automatically — provide the proper sizes for the best results.

## Tips

- Start with 1x first to validate name matching.
- Add 2x and 4x variants as needed for crisp rendering on high-DPI displays.
- Use `--debug-export` to export and inspect bundle contents if you're unsure about the texture names.
