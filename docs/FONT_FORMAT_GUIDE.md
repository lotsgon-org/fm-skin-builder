# Font Format Guide - OTF vs TTF

## Quick Summary

**Good news**: Unity can often handle format mismatches! You can usually replace OTF fonts with TTF files (and vice versa) without issues.

**Default behavior**: The font system is permissive - it warns about format mismatches but allows them.

**Options available**:
- **Permissive mode** (default): Allows format mismatches with info messages
- **Auto-convert mode**: Automatically converts fonts to match original format
- **Strict mode**: Blocks format mismatches (for maximum safety)

## Understanding Font Formats

### OTF (OpenType Font)
- Uses **CFF (Compact Font Format)** tables for glyph data
- Original FM26 fonts: `GT-America-Standard-Black`, `ABCSocial-Regular`
- File signature: `OTTO` (magic bytes)

### TTF (TrueType Font)
- Uses **glyf** tables for glyph data
- Original FM26 fonts: `NotoSans-Regular`
- File signature: `\x00\x01\x00\x00` or `true` (magic bytes)

## Usage Modes

### Mode 1: Permissive (Default) ✅ Recommended

**What it does**: Allows any format, Unity handles compatibility

```json
{
  "includes": ["fonts"]
}
```

**Behavior**:
```
assets/fonts/
  GT-America-Standard-Black.ttf  ← TTF replacing OTF

Output:
ℹ️  Format mismatch for 'GT-America-Standard-Black.ttf':
   original is OTF, replacement is TTF.
   Unity will attempt to use it (may work fine).
✓ Replaced font: GT-America-Standard-Black (GT-America-Standard-Black.ttf)
```

**When to use**: Default choice - works most of the time, maximum flexibility

### Mode 2: Auto-Convert

**What it does**: Automatically converts fonts to match original format

**Setup**: Add config option (future feature):
```json
{
  "includes": ["fonts"],
  "font_options": {
    "auto_convert": true
  }
}
```

**Behavior**:
```
assets/fonts/
  GT-America-Standard-Black.ttf  ← TTF will be converted to OTF

Output:
ℹ️  Auto-converting 'GT-America-Standard-Black.ttf' from TTF to OTF
✓ Converted font: GT-America-Standard-Black_converted.otf
✓ Replaced font: GT-America-Standard-Black
```

**When to use**:
- You have TTF fonts but want perfect format matching
- You're experiencing rendering issues with format mismatches
- Maximum compatibility needed

**Requirements**: `fonttools` package (automatically installed)

### Mode 3: Strict

**What it does**: Blocks format mismatches entirely

**Setup**: Add config option (future feature):
```json
{
  "includes": ["fonts"],
  "font_options": {
    "strict_format": true
  }
}
```

**Behavior**:
```
assets/fonts/
  GT-America-Standard-Black.ttf  ← TTF replacing OTF - BLOCKED

Output:
❌ Format mismatch (strict mode): original is OTF, replacement is TTF.
   Use auto_convert=True or disable strict_format.
Skipping font 'GT-America-Standard-Black': Format mismatch...
```

**When to use**:
- You want absolute certainty about format matching
- You're willing to manually convert fonts
- You prefer explicit failures over silent issues

## How UABEA Does It

The UABEA tool's "Import .ttf/.otf" plugin:
1. Loads the Unity Font asset
2. Replaces `m_FontData` with new font bytes
3. Keeps `m_Name` unchanged (so USS/UXML keeps working)
4. Reserializes to Unity format
5. **Allows any format** - lets Unity handle compatibility

Our tool mimics this exactly in **permissive mode**.

## Conversion Details

When auto-convert is enabled, the tool uses `fonttools` to convert between formats:

### TTF → OTF Conversion
- Reads TTF glyf tables
- Converts to CFF format (complex operation)
- Saves as OTF with proper structure

### OTF → TTF Conversion
- Reads OTF CFF tables
- Converts to glyf format
- Saves as TTF with proper structure

**Note**: Conversion quality depends on font complexity. Simple fonts convert perfectly, complex fonts may lose some hints/features.

## Recommendations

### For Most Users
✅ **Use permissive mode** (default)
- Just drop fonts in `assets/fonts/`
- Let Unity handle format differences
- Fastest workflow

### For Maximum Compatibility
✅ **Use auto-convert mode**
- Fonts are automatically converted to match originals
- No manual conversion needed
- Requires `fonttools`

### For Safety-First Approach
✅ **Use strict mode + manual conversion**
- Manually convert fonts to match originals using:
  - Online tools (CloudConvert, FontForge)
  - Desktop tools (FontForge, Glyphs)
  - Command line: `fonttools ttLib.woff2 compress input.ttf`
- Strict mode ensures perfect format matching

## Real-World Examples

### Example 1: Replacing with Any Format (Permissive)

```
my-skin/
  assets/
    fonts/
      GT-America-Standard-Black.ttf  ← Your TTF font
      ABCSocial-Regular.otf          ← Your OTF font
      NotoSans-Regular.ttf           ← Your TTF font
  config.json
```

```json
{
  "includes": ["fonts"]
}
```

```bash
fm-skin-builder patch my-skin --out build
```

**Result**: All fonts replaced, Unity handles format differences ✅

### Example 2: Auto-Converting Mismatches

Same setup, but with auto-convert:

```json
{
  "includes": ["fonts"],
  "font_options": {
    "auto_convert": true
  }
}
```

**Result**:
- `GT-America-Standard-Black.ttf` converted to OTF automatically
- `ABCSocial-Regular.otf` used as-is (already OTF)
- `NotoSans-Regular.ttf` used as-is (already TTF)

### Example 3: Explicit Mapping with Conversion

```json
{
  "includes": ["fonts"],
  "font_options": {
    "auto_convert": true
  }
}
```

```
assets/fonts/
  CustomFont.ttf
  font-mapping.json
```

`font-mapping.json`:
```json
{
  "GT-America-Standard-Black": "CustomFont.ttf",
  "ABCSocial-Regular": "CustomFont.ttf"
}
```

**Result**: Both fonts replaced with `CustomFont.ttf`, auto-converted as needed

## Troubleshooting

### Font Doesn't Show in Game

**Possible causes**:
1. Font name mismatch (check bundle for exact name)
2. Font file corrupted
3. Very rare: Format incompatibility

**Solutions**:
1. Use catalogue command to find exact font names
2. Try auto-convert mode
3. Try different font file

### Conversion Fails

**Error**: `fonttools not installed`
**Solution**: Should be installed automatically, but if not:
```bash
pip install fonttools
```

**Error**: `Font conversion failed: ...`
**Solution**: Font may be too complex, try:
1. Simplify font using FontForge
2. Use different source font
3. Manually convert with professional tool

### Format Detection Issues

**Error**: `Unable to detect font format (invalid magic bytes)`
**Solution**: Font file may be:
- Corrupted
- Compressed (WOFF/WOFF2) - decompress first
- Not a valid font file

## Technical Details

### Magic Bytes Reference

| Format | Magic Bytes | Hex |
|--------|-------------|-----|
| TTF v1 | `\x00\x01\x00\x00` | 00 01 00 00 |
| TTF Mac | `true` | 74 72 75 65 |
| OTF | `OTTO` | 4F 54 54 4F |

### Unity Font Asset Structure

```
Unity Font Asset:
  m_Name: "GT-America-Standard-Black"  ← Must stay unchanged!
  m_FontData: [binary font bytes]      ← What we replace
  m_LineSpacing: ...
  m_CharacterSpacing: ...
  [other properties]
```

**Critical**: Keep `m_Name` unchanged so USS/UXML references keep working.

### Font Table Comparison

| Aspect | TTF | OTF |
|--------|-----|-----|
| Glyph Data | glyf table | CFF/CFF2 table |
| Compression | None | CFF is inherently compressed |
| Hinting | TrueType hinting | PostScript hinting |
| File Size | Usually larger | Usually smaller |

## FAQ

**Q: Can I use WOFF/WOFF2 fonts?**
A: Not directly. Decompress to TTF/OTF first.

**Q: Will conversion lose font features?**
A: Simple fonts: No. Complex fonts: Some hinting may be lost.

**Q: Which mode should I use?**
A: Start with permissive (default). If issues occur, try auto-convert.

**Q: Can I add NEW fonts to the bundle?**
A: Not yet - this is a future feature. Currently only replaces existing fonts.

**Q: Do I need to edit USS/UXML files?**
A: No! As long as you keep the same font name, existing references work.

**Q: What if the original font was OTF and I only have TTF?**
A: Permissive mode: Just use it, Unity usually handles it.
Auto-convert mode: Tool converts TTF→OTF automatically.

## Future Enhancements

Planned improvements:
- [ ] WOFF/WOFF2 support (auto-decompress)
- [ ] Font subsetting (reduce file size)
- [ ] Adding NEW fonts to bundles
- [ ] Variable font support
- [ ] Font feature preservation in conversion

## See Also

- [FONT_IMPLEMENTATION_PLAN.md](FONT_IMPLEMENTATION_PLAN.md) - Technical implementation details
- [SKIN_FORMAT.md](SKIN_FORMAT.md) - Skin configuration format
- [CLI_GUIDE.md](CLI_GUIDE.md) - Command line usage
