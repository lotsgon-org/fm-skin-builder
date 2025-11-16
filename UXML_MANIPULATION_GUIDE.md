# UXML Manipulation Guide

Complete guide to editing Unity UI Toolkit layouts using the UXML import/export pipeline.

---

## Overview

The UXML pipeline allows you to:
- ✅ Export VTA to human-readable UXML
- ✅ Edit UXML in any text editor
- ✅ Import modified UXML back to VTA format
- ✅ Maintain perfect order and structure
- ✅ Manipulate classes and inline styles

---

## Table of Contents

1. [CSS Classes](#css-classes)
2. [Inline Styles](#inline-styles)
3. [Element Manipulation](#element-manipulation)
4. [Complete Examples](#complete-examples)

---

## CSS Classes

Unity UI Toolkit uses USS (Unity Style Sheets) files for styling, similar to CSS. Elements reference styles using class names.

### How It Works

Elements can have multiple CSS classes:

```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
  <ui:VisualElement name="container" class="main-container dark-theme">
    <ui:Label text="Title" class="title-text large bold"/>
    <ui:Button text="Submit" class="primary-button"/>
  </ui:VisualElement>
</ui:UXML>
```

### USS Files

USS files define the actual styles (managed separately from UXML):

```css
/* BaseStyles.uss */
.title-text {
    font-size: 18px;
    color: #FFFFFF;
}

.large {
    font-size: 24px;
}

.primary-button {
    background-color: #007ACC;
    color: #FFFFFF;
    padding: 10px;
}
```

**Note:** USS files are extracted/patched separately. The UXML only shows which classes are applied.

### Adding Classes

**In UXML (text editing):**
```xml
<!-- Add space-separated class names -->
<ui:Button text="Click Me" class="primary-button large animated"/>
```

**In Python:**
```python
# Find element
button = doc.find_element_by_name("my-button")

# Modify class attribute
for attr in button.attributes:
    if attr.name == 'class':
        classes = attr.value.split()
        classes.append("new-class")
        attr.value = " ".join(classes)
        break
```

### Removing Classes

**In UXML:**
```xml
<!-- Before -->
<ui:Button class="primary-button large active"/>

<!-- After (removed 'active') -->
<ui:Button class="primary-button large"/>
```

**In Python:**
```python
for attr in element.attributes:
    if attr.name == 'class':
        classes = attr.value.split()
        classes.remove("active")
        attr.value = " ".join(classes)
        break
```

### Modifying Classes

**Replace all classes:**
```xml
<!-- Before -->
<ui:Label class="old-style deprecated"/>

<!-- After -->
<ui:Label class="new-style modern"/>
```

---

## Inline Styles

Inline styles are CSS-like style declarations directly on elements. They override styles from USS classes.

### How It Works

Inline styles use the `style` attribute:

```xml
<ui:Label text="Hello"
          class="title-text"
          style="color: #FF0000; font-size: 24px;"/>
```

**Priority:** Inline styles override USS class styles (like HTML/CSS).

### Syntax

```
style="property1: value1; property2: value2;"
```

**Common Properties:**
- `color: #RRGGBB` or `rgb(r, g, b)`
- `font-size: 16px`
- `font-weight: bold`
- `background-color: #FFFFFF`
- `margin: 10px` or `margin-left: 5px`
- `padding: 10px`
- `width: 200px` or `width: 50%`
- `height: 100px`
- `flex-direction: row`
- `align-items: center`
- `justify-content: space-between`

### Examples

**Simple styling:**
```xml
<ui:Button text="Click Me"
           class="primary-button"
           style="background-color: #FF5722;"/>
```

**Layout properties:**
```xml
<ui:VisualElement style="flex-direction: row; padding: 10px;">
  <ui:Label text="Name:" style="width: 100px;"/>
  <ui:TextField style="flex-grow: 1;"/>
</ui:VisualElement>
```

**Overriding class styles:**
```xml
<!-- USS defines .title-text with color: #FFFFFF -->
<!-- Inline style overrides to make it red -->
<ui:Label class="title-text" style="color: #FF0000;"/>
```

### When to Use

**Use Classes (in USS files):**
- Reusable styles across many elements
- Theme-level styling
- Consistent design patterns

**Use Inline Styles:**
- One-off overrides
- Dynamic/computed values
- Quick prototyping
- Element-specific adjustments

### Programmatic Manipulation

**Python API:**
```python
from fm_skin_builder.core.uxml.uxml_importer import UXMLImporter
from fm_skin_builder.core.uxml.uxml_exporter import UXMLExporter
from fm_skin_builder.core.uxml.uxml_ast import UXMLAttribute
from pathlib import Path

# Import UXML
importer = UXMLImporter()
doc = importer.import_uxml(Path("layout.uxml"))

# Find element and modify style
label = doc.find_element_by_name("my-label")
for attr in label.attributes:
    if attr.name == 'style':
        attr.value = "color: #00FF00; font-size: 32px;"
        break
else:
    # Add style if it doesn't exist
    label.attributes.append(UXMLAttribute(
        name="style",
        value="color: #00FF00; font-size: 32px;"
    ))

# Export back
exporter = UXMLExporter()
exporter.write_uxml(doc, Path("layout_modified.uxml"))
```

---

## Element Manipulation

Add, remove, or modify UI elements in the hierarchy.

### Adding Elements

**In UXML (text editing):**
```xml
<ui:VisualElement name="container">
  <ui:Label text="Existing element"/>

  <!-- Add a new button -->
  <ui:Button name="new-btn" text="Click Me" class="primary-button"/>

  <!-- Add a text field -->
  <ui:TextField name="input" placeholder-text="Enter text..."/>
</ui:VisualElement>
```

**In Python:**
```python
from fm_skin_builder.core.uxml.uxml_ast import UXMLElement, UXMLAttribute

# Create new element
new_button = UXMLElement(
    element_type="Button",
    attributes=[
        UXMLAttribute(name="name", value="new-btn"),
        UXMLAttribute(name="text", value="Click Me"),
        UXMLAttribute(name="class", value="primary-button"),
    ]
)

# Add to parent
container = doc.find_element_by_name("container")
container.children.append(new_button)
```

### Removing Elements

**In UXML:**
```xml
<!-- Just delete the element -->
<ui:VisualElement name="container">
  <ui:Label text="Keep this"/>
  <!-- Deleted: <ui:Button name="remove-me"/> -->
  <ui:TextField text="Keep this too"/>
</ui:VisualElement>
```

**In Python:**
```python
# Remove by index
container.children.pop(1)

# Remove by finding element
for i, child in enumerate(container.children):
    if child.get_attribute("name") == "remove-me":
        container.children.pop(i)
        break

# Remove all elements of a type
container.children = [
    child for child in container.children
    if child.element_type != "Button"
]
```

### Modifying Elements

**Change attributes:**
```xml
<!-- Before -->
<ui:Button name="btn1" text="Old Text" class="primary"/>

<!-- After -->
<ui:Button name="btn1" text="New Text" class="primary disabled"/>
```

**Python:**
```python
button = doc.find_element_by_name("btn1")

# Modify existing attribute
for attr in button.attributes:
    if attr.name == "text":
        attr.value = "New Text"
    elif attr.name == "class":
        attr.value += " disabled"

# Add new attribute
button.attributes.append(UXMLAttribute(
    name="tooltip",
    value="Click to submit"
))
```

### Moving Elements

**In UXML (cut and paste):**
```xml
<!-- Before -->
<ui:VisualElement name="left-panel">
  <ui:Button name="move-me" text="I will move"/>
</ui:VisualElement>
<ui:VisualElement name="right-panel">
</ui:VisualElement>

<!-- After -->
<ui:VisualElement name="left-panel">
</ui:VisualElement>
<ui:VisualElement name="right-panel">
  <ui:Button name="move-me" text="I will move"/>
</ui:VisualElement>
```

**In Python:**
```python
# Find source and destination
left_panel = doc.find_element_by_name("left-panel")
right_panel = doc.find_element_by_name("right-panel")

# Move element
button = left_panel.children.pop(0)
right_panel.children.append(button)
```

### Reordering Elements

**In UXML:**
```xml
<!-- Order matters! Elements render in document order -->
<ui:VisualElement>
  <ui:Label text="First"/>
  <ui:Button text="Second"/>
  <ui:TextField text="Third"/>
</ui:VisualElement>
```

**In Python:**
```python
# Swap two elements
container.children[0], container.children[1] = \
    container.children[1], container.children[0]

# Sort by name
container.children.sort(
    key=lambda e: e.get_attribute("name") or ""
)

# Move to front
element = container.children.pop(2)
container.children.insert(0, element)
```

---

## Complete Examples

### Example 1: Class Override with Inline Style

```python
from fm_skin_builder.core.uxml.uxml_importer import UXMLImporter
from fm_skin_builder.core.uxml.uxml_exporter import UXMLExporter
from pathlib import Path

# Import UXML
importer = UXMLImporter()
doc = importer.import_uxml(Path("panel.uxml"))

# Find all buttons with "primary-button" class
# Override one with red background
for i, button in enumerate(doc.find_elements_by_class("primary-button")):
    if i == 0:  # Only the first button
        # Add inline style to override
        from fm_skin_builder.core.uxml.uxml_ast import UXMLAttribute
        button.attributes.append(UXMLAttribute(
            name="style",
            value="background-color: #FF0000;"
        ))

# Export
exporter = UXMLExporter()
exporter.write_uxml(doc, Path("panel_updated.uxml"))
```

**Result UXML:**
```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements">
  <!-- First button gets red background override -->
  <ui:Button class="primary-button" style="background-color: #FF0000;"/>
  <!-- Others keep USS class style -->
  <ui:Button class="primary-button"/>
  <ui:Button class="primary-button"/>
</ui:UXML>
```

---

### Example 2: Dynamic Form Builder

```python
from fm_skin_builder.core.uxml.uxml_ast import UXMLElement, UXMLAttribute

# Import base template
doc = importer.import_uxml(Path("form_template.uxml"))
container = doc.find_element_by_name("form-container")

# Define form fields
fields = [
    {"label": "Name", "type": "TextField", "placeholder": "Enter your name"},
    {"label": "Email", "type": "TextField", "placeholder": "you@example.com"},
    {"label": "Age", "type": "IntegerField", "placeholder": "0"},
]

# Add fields dynamically
for field_def in fields:
    # Create row
    row = UXMLElement(
        element_type="VisualElement",
        attributes=[UXMLAttribute(name="class", value="form-row")]
    )

    # Add label
    label = UXMLElement(
        element_type="Label",
        attributes=[
            UXMLAttribute(name="text", value=field_def["label"]),
            UXMLAttribute(name="class", value="form-label"),
        ]
    )
    row.children.append(label)

    # Add input
    input_field = UXMLElement(
        element_type=field_def["type"],
        attributes=[
            UXMLAttribute(name="placeholder-text", value=field_def["placeholder"]),
            UXMLAttribute(name="class", value="form-input"),
        ]
    )
    row.children.append(input_field)

    # Add row to container
    container.children.append(row)

# Add submit button
submit = UXMLElement(
    element_type="Button",
    attributes=[
        UXMLAttribute(name="text", value="Submit"),
        UXMLAttribute(name="class", value="submit-button"),
    ]
)
container.children.append(submit)

# Export
exporter.write_uxml(doc, Path("form_generated.uxml"))
```

**Result UXML:**
```xml
<ui:VisualElement name="form-container" class="form-container">
  <ui:VisualElement class="form-row">
    <ui:Label text="Name" class="form-label"/>
    <ui:TextField placeholder-text="Enter your name" class="form-input"/>
  </ui:VisualElement>
  <ui:VisualElement class="form-row">
    <ui:Label text="Email" class="form-label"/>
    <ui:TextField placeholder-text="you@example.com" class="form-input"/>
  </ui:VisualElement>
  <ui:VisualElement class="form-row">
    <ui:Label text="Age" class="form-label"/>
    <ui:IntegerField placeholder-text="0" class="form-input"/>
  </ui:VisualElement>
  <ui:Button text="Submit" class="submit-button"/>
</ui:VisualElement>
```

---

### Example 3: Theme Switcher (Inline Style Override)

```python
# Import
doc = importer.import_uxml(Path("dialog.uxml"))

# Apply dark theme using inline style overrides
dark_theme = {
    "Label": "color: #FFFFFF; background-color: #2D2D30;",
    "Button": "color: #FFFFFF; background-color: #007ACC;",
    "TextField": "color: #FFFFFF; background-color: #3E3E42; border-color: #555555;",
}

for element_type, style_value in dark_theme.items():
    elements = doc.find_elements_by_type(element_type)
    for elem in elements:
        # Add or update style attribute
        found = False
        for attr in elem.attributes:
            if attr.name == "style":
                attr.value = style_value
                found = True
                break
        if not found:
            from fm_skin_builder.core.uxml.uxml_ast import UXMLAttribute
            elem.attributes.append(UXMLAttribute(
                name="style",
                value=style_value
            ))

# Export
exporter.write_uxml(doc, Path("dialog_dark.uxml"))
```

---

### Example 4: Bulk Class Updates

```python
# Import
doc = importer.import_uxml(Path("complex_panel.uxml"))

# Update naming convention for all elements
for element in doc.get_all_elements():
    # Update class names (old -> new convention)
    for attr in element.attributes:
        if attr.name == "class":
            # Replace old class prefix with new
            attr.value = attr.value.replace("old-", "new-")
            # Add version suffix
            classes = attr.value.split()
            classes.append("v2")
            attr.value = " ".join(classes)

# Export
exporter.write_uxml(doc, Path("complex_panel_updated.uxml"))
```

---

## Best Practices

### 1. **Use USS for Reusable Styles**
```xml
<!-- Good: Reusable, maintainable -->
<ui:Button class="primary-button"/>
<ui:Button class="primary-button"/>

<!-- Avoid: Duplicated inline styles -->
<ui:Button style="color: #FFF; background: #007ACC; padding: 10px;"/>
<ui:Button style="color: #FFF; background: #007ACC; padding: 10px;"/>
```

### 2. **Use Inline Styles for Overrides**
```xml
<!-- Good: Base style from USS, specific override inline -->
<ui:Label class="title-text" style="color: #FF0000;"/>

<!-- Avoid: Everything inline when it could be in USS -->
<ui:Label style="font-size: 24px; font-weight: bold; margin: 10px; color: #FF0000;"/>
```

### 3. **Maintain Semantic Class Names**
```xml
<!-- Good: Describes purpose -->
<ui:Button class="submit-button primary"/>

<!-- Avoid: Describes appearance -->
<ui:Button class="blue-button big"/>
```

### 4. **Keep Element Hierarchy Flat**
```xml
<!-- Good: Shallow hierarchy -->
<ui:VisualElement class="container">
  <ui:Label class="title"/>
  <ui:Button class="action"/>
</ui:VisualElement>

<!-- Avoid: Deep nesting (unless necessary) -->
<ui:VisualElement>
  <ui:VisualElement>
    <ui:VisualElement>
      <ui:Label/>
    </ui:VisualElement>
  </ui:VisualElement>
</ui:VisualElement>
```

### 5. **Use Names for Important Elements**
```xml
<!-- Good: Named for programmatic access -->
<ui:Button name="submit-btn" text="Submit"/>

<!-- OK: No name needed if not referenced -->
<ui:Label text="Description"/>
```

---

## Workflow Integration

### With CSS Patcher

The UXML pipeline works perfectly with your existing CSS patcher:

1. **Export UXML** - See class names
2. **Export USS** - See style definitions
3. **Edit UXML** - Add/remove classes or inline overrides
4. **Patch USS** - Modify style definitions (via CSS patcher)
5. **Import Both** - Reimport UXML and USS

**Example:**
```xml
<!-- UXML: Shows which classes are used -->
<ui:Label class="item-name highlight"/>
```

```css
/* USS: Defines what those classes do (patched separately) */
.item-name {
    font-size: 14px;
    color: #FFFFFF;
}

.highlight {
    background-color: #FFD700;
    font-weight: bold;
}
```

---

## Summary

| Feature | Support | Notes |
|---------|---------|-------|
| CSS Classes | ✅ Full | Class names reference USS files |
| Inline Styles | ✅ Full | Override USS classes |
| Class Add/Remove | ✅ Full | Simple text editing |
| Element Add/Remove | ✅ Full | Python or UXML editing |
| Element Reorder | ✅ Full | Order preserved perfectly |
| Attribute Editing | ✅ Full | All attributes supported |
| Template References | ✅ Full | See TEMPLATE_AND_ORDER_FIXES_COMPLETE.md |
| Data Bindings | ✅ Full | See BINDING_EXTRACTION_COMPLETE.md |
| USS Content | ➡️ Separate Tool | Use USS exporter/patcher |

---

## Key Takeaways

1. **Classes** - Use for reusable styles defined in USS files
2. **Inline Styles** - Use for element-specific overrides
3. **Human Readable** - Clean UXML with no GUID clutter
4. **USS Separate** - Style definitions managed via USS exporter/patcher
5. **Full Control** - Add/remove/modify classes and elements easily

Happy editing! 🎨
