# UXML Import/Export Pipeline

## Overview

The UXML import/export pipeline enables full round-trip editing of Football Manager 2026's Unity UI Toolkit interfaces. This system allows skin authors to:

1. **Export** UXML files from Unity bundles to human-readable XML
2. **Edit** the UXML in any text editor or specialized tool
3. **Import** modified UXML back into Unity bundles safely

This implementation is built on top of the existing asset catalogue system and bundle patcher, ensuring compatibility with FM26's architecture.

---

## Architecture

### Components

The UXML pipeline consists of five main components:

#### 1. UXML AST (`fm_skin_builder/core/uxml/uxml_ast.py`)

Data structures representing UXML documents in a format that can be:
- Serialized to XML text
- Deserialized from XML text
- Converted to/from Unity's VisualTreeAsset format

**Key Classes:**
- `UXMLDocument`: Complete UXML document with metadata
- `UXMLElement`: Individual UI element (VisualElement, Label, Button, etc.)
- `UXMLAttribute`: Element attributes (name, class, style, etc.)
- `UXMLTemplate`: Template references for reusable UI fragments
- `StyleRule`: CSS style rules
- `InlineStyle`: Inline style properties

#### 2. UXML Exporter (`fm_skin_builder/core/uxml/uxml_exporter.py`)

Converts Unity's VisualTreeAsset objects to UXML text.

**Process:**
1. Traverse VisualElementAsset hierarchy (DFS)
2. Extract attributes from UxmlTraits
3. Rebuild element tree structure
4. Extract template references
5. Parse inline StyleSheet (if present)
6. Generate pretty-printed UXML XML

#### 3. UXML Importer (`fm_skin_builder/core/uxml/uxml_importer.py`)

Converts UXML text back to Unity's VisualTreeAsset format.

**Process:**
1. Parse XML into AST
2. Convert AST to Unity structures:
   - `m_VisualElementAssets` array
   - `m_Strings` string table
   - `m_TemplateAssets` template references
   - `m_InlineSheet` StyleSheet (if needed)
3. Inject modified VTA into bundle
4. Preserve GUIDs, FileIDs, and PathIDs

#### 4. Style Parser (`fm_skin_builder/core/uxml/style_parser.py`)

Converts Unity StyleSheet objects to CSS text.

**Handles:**
- All Unity value types (color, dimension, float, string, variable, resource)
- Complex selectors (class, ID, type, pseudo-class, combinators)
- CSS variables (`var(--name)`)
- Multi-value properties

#### 5. Style Serializer (`fm_skin_builder/core/uxml/style_serializer.py`)

Converts CSS text back to Unity StyleSheet structures.

**Handles:**
- CSS property parsing
- Value type inference
- Color conversion (hex → RGBA)
- Variable reference preservation
- Selector parsing and conversion

---

## Unity Data Structures

### VisualTreeAsset

Unity stores UXML as compiled VisualTreeAsset objects with these key fields:

```
m_Name: string
m_VisualElementAssets: array
  - id: int
  - parentId: int
  - orderInDocument: int
  - m_TypeName: string
  - m_Name: int (string index)
  - m_Classes: array of int (string indices)
  - m_Text: int (string index)
m_TemplateAssets: array
  - m_Name: string
  - m_FileID: int
  - guid: string
m_Strings: array of string
m_InlineSheet: StyleSheet (optional)
```

### StyleSheet

Inline styles are stored as separate StyleSheet objects:

```
strings: array of string
colors: array of Color (r, g, b, a floats)
m_Rules: array
  - m_Properties: array
    - m_Name: string
    - m_Values: array
      - m_ValueType: int (1-10)
      - valueIndex: int
      - value: varies by type
m_ComplexSelectors: array
  - ruleIndex: int
  - m_Selectors: array
    - m_Parts: array
      - m_Type: int (0-6)
      - m_Value: string
```

---

## Usage

### Exporting UXML

```python
from fm_skin_builder.core.uxml import UXMLExporter
import UnityPy

# Load bundle
env = UnityPy.load("skins.bundle")

# Find VisualTreeAsset
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        data = obj.read()
        if hasattr(data, "m_VisualElementAssets"):
            # Export to UXML
            exporter = UXMLExporter()
            doc = exporter.export_visual_tree_asset(
                data,
                output_path=Path("output/MainMenu.uxml")
            )
```

### Importing UXML

```python
from fm_skin_builder.core.uxml import UXMLImporter
from pathlib import Path

# Import from file
importer = UXMLImporter()
doc = importer.import_uxml(Path("output/MainMenu.uxml"))

# Inject into bundle
importer.inject_into_bundle(
    doc,
    bundle_path=Path("skins.bundle"),
    output_path=Path("skins_modified.bundle")
)
```

### Editing UXML

Once exported, UXML can be edited like any XML file:

```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
  <ui:VisualElement name="root" class="main-menu">
    <ui:Label text="Main Menu" class="title" />
    <ui:Button text="Start Game" class="primary-button" />
    <ui:Button text="Options" class="secondary-button" />
  </ui:VisualElement>
</ui:UXML>
```

**Supported edits:**
- Add/remove/reorder elements
- Modify attributes (name, class, text, etc.)
- Change element types
- Add/remove CSS classes
- Modify inline styles (in comments)

---

## Integration with Asset Catalogue

The UXML system integrates with the asset catalogue through the `UXMLExtractor`:

```python
from fm_skin_builder.core.catalogue.extractors import UXMLExtractor

# Create extractor
extractor = UXMLExtractor(
    fm_version="2026.4.0",
    export_uxml=True,
    export_dir=Path("output")
)

# Extract from bundle
vta_assets = extractor.extract_from_bundle(Path("skins.bundle"))

# Each VTA asset includes:
# - name, bundle, content_hash
# - element_count, element_types
# - classes_used, templates_used
# - has_inline_styles, tags
# - export_path (if exported)
```

Catalogue entries for VisualTreeAssets:

```json
{
  "name": "MainMenu",
  "bundle": "skins.bundle",
  "content_hash": "a1b2c3...",
  "element_count": 15,
  "element_types": ["VisualElement", "Label", "Button"],
  "classes_used": ["main-menu", "title", "primary-button"],
  "templates_used": ["HeaderTemplate"],
  "has_inline_styles": true,
  "tags": ["menu", "ui", "screen"],
  "export_path": "uxml/MainMenu.uxml",
  "status": "active",
  "first_seen": "2026.4.0",
  "last_seen": "2026.4.0"
}
```

---

## Bundle Injection

The importer uses UnityPy to safely inject modified assets:

1. **Locate target asset** by name in bundle
2. **Rebuild Unity structures** from UXML document
3. **Update asset in place**, preserving:
   - GUID (Globally Unique Identifier)
   - FileID (file reference)
   - PathID (object path)
4. **Save modified bundle** with Unity's save format

This ensures FM26 can load the modified bundle without errors.

---

## Template Handling

UXML templates are reusable UI fragments:

### Export
```xml
<Template name="ButtonTemplate" src="Buttons.uxml" />
```

### Import
- Verifies template exists via catalogue
- Maintains stable GUID/FileID references
- Preserves template dependency graph

---

## Style Handling

### Inline Styles

Exported as XML comments for easy editing:

```xml
<!--
  Inline Styles:
  .button {
    background-color: #1976d2;
    color: #ffffff;
    padding: 10px;
  }
-->
```

When reimported, these are converted back to Unity's StyleSheet format.

### CSS Variables

Fully supported in both directions:

```css
:root {
  --primary-color: #1976d2;
  --button-padding: 10px;
}

.button {
  background-color: var(--primary-color);
  padding: var(--button-padding);
}
```

---

## Platform Considerations

FM26 bundles differ between Windows and macOS, but the UXML pipeline is platform-agnostic:

- **Export**: Works on any platform's bundles
- **Import**: Generates platform-neutral Unity structures
- **Deployment**: Use existing bundle patcher to create platform-specific builds

---

## Testing

Comprehensive round-trip tests ensure data integrity:

### Test Categories

1. **Element Structure Tests**
   - Simple elements
   - Nested hierarchies
   - Text content

2. **Attribute Tests**
   - Name, class, style attributes
   - Class manipulation
   - Custom attributes

3. **Style Tests**
   - CSS parsing
   - Value type serialization
   - Selector parsing
   - Variables and resources

4. **Round-trip Tests**
   - Export → Import → Export consistency
   - Content hash stability
   - Unity structure preservation

Run tests:
```bash
pytest tests/uxml/test_roundtrip.py -v
```

---

## Limitations & Future Work

### Current Limitations

1. **Custom Element Types**: Only standard Unity UI Toolkit elements are fully supported
2. **SI Custom Elements**: Sports Interactive's custom elements may need special handling
3. **Complex Inline Styles**: Some advanced USS features may not round-trip perfectly
4. **Bindings**: Data bindings are not yet extracted (Unity's binding system is complex)

### Future Enhancements

1. **Visual Editor**: Web-based UXML editor with preview
2. **Template Library**: Searchable template catalogue
3. **Live Reload**: Hot-reload UXML changes in-game (dev mode)
4. **Validation**: Pre-import validation of UXML structure
5. **Diffing**: Visual diff tool for UXML changes between versions

---

## File Structure

```
fm_skin_builder/
├── core/
│   └── uxml/
│       ├── __init__.py
│       ├── uxml_ast.py           # AST data structures
│       ├── uxml_exporter.py      # VTA → UXML
│       ├── uxml_importer.py      # UXML → VTA
│       ├── style_parser.py       # StyleSheet → CSS
│       └── style_serializer.py   # CSS → StyleSheet
├── core/catalogue/
│   ├── models.py                 # Added VisualTreeAsset model
│   └── extractors/
│       └── uxml_extractor.py     # Catalogue integration
tests/
└── uxml/
    ├── __init__.py
    └── test_roundtrip.py         # Round-trip tests
```

---

## API Reference

### UXMLExporter

```python
class UXMLExporter:
    def export_visual_tree_asset(
        vta_data: Any,
        output_path: Optional[Path] = None
    ) -> UXMLDocument

    def write_uxml(
        doc: UXMLDocument,
        output_path: Path
    ) -> None
```

### UXMLImporter

```python
class UXMLImporter:
    def import_uxml(
        uxml_path: Path
    ) -> UXMLDocument

    def import_uxml_text(
        uxml_text: str,
        asset_name: str = "Imported"
    ) -> UXMLDocument

    def build_visual_tree_asset(
        doc: UXMLDocument,
        base_vta: Optional[Any] = None
    ) -> Dict[str, Any]

    def inject_into_bundle(
        doc: UXMLDocument,
        bundle_path: Path,
        output_path: Path
    ) -> None
```

### StyleParser

```python
class StyleParser:
    def parse_stylesheet(
        stylesheet_data: Any
    ) -> str

    def parse_inline_styles(
        element_data: Any,
        strings: List[str],
        colors: List[Any]
    ) -> str
```

### StyleSerializer

```python
class StyleSerializer:
    def parse_css(
        css_text: str
    ) -> List[Dict[str, Any]]

    def build_stylesheet_data(
        rules: List[Dict[str, Any]],
        base_stylesheet: Optional[Any] = None
    ) -> Tuple[List[str], List[Any], List[Any], List[Any]]
```

---

## Changelog

### v1.0.0 (2025-01-15)
- Initial implementation of UXML import/export pipeline
- Full round-trip support for VisualTreeAsset
- Style parsing and serialization
- Asset catalogue integration
- Comprehensive test suite

---

## Contributing

When working with UXML:

1. **Preserve Unity structures**: Always maintain GUIDs, FileIDs, and internal indices
2. **Test round-trips**: Ensure export → import → export produces identical results
3. **Validate styles**: Check that CSS converts correctly to Unity's format
4. **Document edge cases**: Note any special handling needed for specific elements

---

## References

- [Unity UI Toolkit Documentation](https://docs.unity3d.com/Manual/UIElements.html)
- [Unity Serialization Format](https://docs.unity3d.com/Manual/script-Serialization.html)
- [UnityPy Library](https://github.com/K0lb3/UnityPy)
- FM Skin Builder Asset Catalogue System

---

## Support

For issues or questions about the UXML pipeline:

1. Check test cases in `tests/uxml/test_roundtrip.py`
2. Review API documentation above
3. Examine example UXML exports in `output/uxml/`
4. Report issues with sample UXML and bundle info
