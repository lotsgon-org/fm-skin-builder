# CSS/USS Asset Catalogue Expansion

## Overview

This document describes the comprehensive expansion of the FM Skin Builder asset catalogue system to fully support **CSS/USS class introspection**, **dependency mapping**, **advanced search**, and **property-level diffing**.

## Schema Version: 2.2.0

The catalogue schema has been upgraded from **2.1.0** to **2.2.0** to support these new features while maintaining backward compatibility.

---

## 🎯 What's New

### 1. Enhanced CSS Class Model

**Previously (Schema 2.1.0):**
- Basic property list with types and values
- Simple variable usage tracking
- Basic tags

**Now (Schema 2.2.0):**
- ✅ **Raw properties** - Property values before variable resolution
- ✅ **Resolved properties** - Property values after variable resolution
- ✅ **Asset dependencies** - Sprite/texture/image references extracted from properties
- ✅ **Color tokens** - All hex color values used (resolved)
- ✅ **Numeric tokens** - All dimension values (px, %, rem, etc.)
- ✅ **Property summary** - Quick overview with colors, assets, variables, and layout

**Example:**
```json
{
  "name": ".player-name",
  "raw_properties": {
    "color": "#FFFFFF",
    "background-color": "var(--club-primary)",
    "border-radius": "4px"
  },
  "resolved_properties": {
    "color": "#FFFFFF",
    "background-color": "#1976D2",
    "border-radius": "4px"
  },
  "asset_dependencies": ["FMImages_1x/star_full"],
  "color_tokens": ["#FFFFFF", "#1976D2"],
  "numeric_tokens": ["4px"],
  "summary": {
    "colors": ["#1976D2", "#FFFFFF"],
    "assets": ["FMImages_1x/star_full"],
    "variables": ["--club-primary"],
    "layout": {
      "border-radius": "4px"
    }
  }
}
```

### 2. Reverse Search Indexes

**New indexes for advanced search capabilities:**

| Index | Description | Use Case |
|-------|-------------|----------|
| `color_to_classes` | Hex color → Classes using that color | "Find all classes using #1976D2" |
| `property_to_classes` | Property name → Classes defining it | "Find all classes with border-radius" |
| `variable_to_classes` | Variable name → Classes using it | "Find all classes using --club-primary" |
| `asset_to_classes` | Asset reference → Classes using it | "Find all classes using star_full sprite" |
| `token_to_classes` | Numeric token → Classes using it | "Find all classes with 4px" |

**Example:**
```json
{
  "css_reverse_indexes": {
    "color_to_classes": {
      "#1976D2": [".player-name", ".link-primary", ".accent-box"]
    },
    "variable_to_classes": {
      "--club-primary": [".player-name", ".team-badge", ".club-colors"]
    },
    "asset_to_classes": {
      "FMImages_1x/star_full": [".player-name", ".rating-indicator"]
    }
  }
}
```

### 3. Property-Level USS Diffing

**Enhanced version comparison with detailed property changes:**

- **Added properties** - New properties in modified classes
- **Removed properties** - Properties removed from classes
- **Modified properties** - Properties with changed values (tracks both raw and resolved)
- **Variable reference changes** - Added/removed variable dependencies
- **Asset dependency changes** - Added/removed sprite/texture references

**Example:**
```json
{
  "asset_type": "css_class",
  "name": ".player-name",
  "change_type": "modified",
  "details": {
    "added_properties": [
      {
        "property": "background-image",
        "value": "sprite://FMImages_1x/star_full"
      }
    ],
    "modified_properties": [
      {
        "property": "border-radius",
        "old_raw": "2px",
        "new_raw": "4px",
        "old_resolved": "2px",
        "new_resolved": "4px"
      }
    ],
    "variable_changes": {
      "added": [],
      "removed": []
    },
    "asset_changes": {
      "added": ["FMImages_1x/star_full"],
      "removed": []
    }
  }
}
```

### 4. Dependency Graphs

**Four comprehensive dependency graphs for visualization:**

#### a) Variable → Classes
Shows which CSS classes use each variable.

```json
{
  "adjacency": {
    "--club-primary": [".player-name", ".team-badge", ".club-colors"]
  },
  "nodes": [
    {
      "id": "--club-primary",
      "type": "variable",
      "stylesheet": "FMColours",
      "usage_count": 3
    }
  ],
  "edges": [
    {
      "from": "--club-primary",
      "to": ".player-name",
      "type": "uses_variable"
    }
  ]
}
```

#### b) Class → Variables
Shows which variables each CSS class uses.

#### c) Sprite → Classes
Shows which CSS classes reference each sprite/asset.

#### d) Variable → Variable
Shows variable dependencies (variables referencing other variables).

---

## 📂 New Files & Modules

### Core Modules

1. **`css_resolver.py`** - Variable resolution and token extraction
   - `CSSResolver` class for resolving var() references
   - Token extractors (colors, numerics, assets)
   - Property summary builder

2. **`dependency_graph.py`** - Dependency graph generation
   - `DependencyGraphBuilder` class
   - Adjacency list generation
   - Node and edge metadata
   - Usage statistics

### Updated Modules

1. **`models.py`**
   - Enhanced `CSSClass` model with new fields
   - Updated schema version to 2.2.0

2. **`css_extractor.py`**
   - Variable resolution during extraction
   - Enhanced class data population
   - Asset dependency extraction

3. **`search_builder.py`**
   - New `_build_css_reverse_indexes()` method
   - Comprehensive reverse indexing

4. **`version_differ.py`**
   - New `_compare_class_properties()` method
   - Property-level change detection
   - Variable and asset change tracking

5. **`exporter.py`**
   - Export dependency graphs to `dependency-graphs.json`
   - Schema 2.2.0 support

6. **`builder.py`**
   - Dependency graph building in Phase 5b
   - Pass graphs to exporter

---

## 📊 Output Files

The catalogue now generates the following JSON files:

| File | Description | Schema |
|------|-------------|--------|
| `metadata.json` | Catalogue metadata | 2.2.0 |
| `css-variables.json` | CSS variables | 2.2.0 |
| `css-classes.json` | **Enhanced** CSS classes | **2.2.0** |
| `sprites.json` | Sprites | 2.1.0 |
| `textures.json` | Textures | 2.1.0 |
| `fonts.json` | Fonts | 2.1.0 |
| `search-index.json` | **Enhanced** search indexes | **2.2.0** |
| `dependency-graphs.json` | **NEW** Dependency graphs | **2.2.0** |

---

## 🔧 Usage

### Building the Catalogue

The catalogue builder automatically includes all new features:

```bash
fm-skin-builder catalogue --fm-version 2026.4.0
```

### Accessing Enhanced Data

#### 1. Search by Color

Find all classes using a specific color:

```python
import json

with open("catalogue/search-index.json") as f:
    index = json.load(f)

classes_with_blue = index["css_reverse_indexes"]["color_to_classes"]["#1976D2"]
# [".player-name", ".link-primary", ".accent-box"]
```

#### 2. Find Variable Usage

Track which classes use a specific variable:

```python
classes_using_var = index["css_reverse_indexes"]["variable_to_classes"]["--club-primary"]
# [".player-name", ".team-badge", ".club-colors"]
```

#### 3. Asset Dependency Tracking

Find classes referencing a specific sprite:

```python
classes_using_sprite = index["css_reverse_indexes"]["asset_to_classes"]["FMImages_1x/star_full"]
# [".player-name", ".rating-indicator", ".favorite-icon"]
```

#### 4. Analyze Variable Dependencies

```python
with open("catalogue/dependency-graphs.json") as f:
    graphs = json.load(f)

# Get all classes using --club-primary
variable_graph = graphs["variable_to_classes"]
usage = variable_graph["adjacency"]["--club-primary"]
# [".player-name", ".team-badge", ".club-colors"]

# Get usage statistics
summary = variable_graph["summary"]
most_used = summary["most_used_variables"]
```

#### 5. Property-Level Diff Analysis

```python
# Load changelog
with open("catalogue/changelog.json") as f:
    changelog = json.load(f)

# Find CSS class modifications
css_class_changes = changelog["changes_by_type"]["css_class"]["modified"]

for change in css_class_changes:
    print(f"Class: {change['name']}")
    print(f"Added properties: {change['details']['added_properties']}")
    print(f"Modified properties: {change['details']['modified_properties']}")
    print(f"Variable changes: {change['details']['variable_changes']}")
```

---

## 🎨 Website Integration

### CSS Class Detail Pages

The enhanced data supports rich class detail pages:

```javascript
// Example: Display class details
{
  className: ".player-name",
  properties: {
    raw: {
      "background-color": "var(--club-primary)"
    },
    resolved: {
      "background-color": "#1976D2"
    }
  },
  dependencies: {
    variables: ["--club-primary"],
    assets: ["FMImages_1x/star_full"]
  },
  summary: {
    colors: ["#FFFFFF", "#1976D2"],
    layout: {
      "border-radius": "4px"
    }
  }
}
```

### USS Diff Viewer

Display property-level changes:

```javascript
// Example: Render property diff
{
  property: "border-radius",
  old: "2px",
  new: "4px",
  type: "modified"
}

{
  property: "background-image",
  value: "sprite://FMImages_1x/star_full",
  type: "added"
}
```

### Dependency Graph Visualization

Use D3.js or similar to visualize:

```javascript
// Load dependency graph
const graph = dependencyGraphs.variable_to_classes;

// Render nodes
graph.nodes.forEach(node => {
  renderNode(node.id, node.type, node.usage_count);
});

// Render edges
graph.edges.forEach(edge => {
  renderEdge(edge.from, edge.to, edge.type);
});
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_css_resolver.py
pytest tests/test_dependency_graph.py
pytest tests/test_search_builder.py
```

### Test Coverage

- ✅ CSS variable resolution
- ✅ Token extraction (colors, numerics, assets)
- ✅ Dependency graph generation
- ✅ Reverse index building
- ✅ Property-level diffing
- ✅ Asset dependency extraction

---

## 📈 Performance

The enhanced catalogue system maintains excellent performance:

- **Extraction**: ~1-2 seconds for typical FM bundles
- **Resolution**: O(n) variable resolution with caching
- **Indexing**: O(n) for all reverse indexes
- **Graph building**: O(n + e) where n = nodes, e = edges

---

## 🔄 Backward Compatibility

The system maintains **full backward compatibility** with schema 2.1.0:

- All new fields are **optional**
- Existing tools continue to work
- Version differ handles both old and new schemas
- Fallback mechanisms for missing enhanced data

---

## 📝 Examples

See the `examples/` directory for complete JSON examples:

- `enhanced-css-class-example.json` - Enhanced CSS class data
- `search-index-example.json` - Reverse search indexes
- `dependency-graphs-example.json` - Dependency graphs
- `changelog-example.json` - Property-level diff output

---

## 🚀 Future Enhancements

Potential future additions:

- **CSS selector specificity calculation**
- **Property inheritance tracking**
- **Cross-bundle dependency analysis**
- **Performance profiling for style application**
- **Automated optimization suggestions**

---

## 📄 License

This expansion is part of the FM Skin Builder project.

---

## 🙏 Acknowledgments

Built with:
- UnityPy for Unity asset parsing
- Pydantic for data validation
- Python 3.11+ for modern language features
