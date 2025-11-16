# Template and Ordering Fixes - Complete ✅

## Summary

All requested fixes have been implemented and tested. The UXML pipeline now correctly handles:
1. ✅ **Template references** - You can see and move nested UXML files
2. ✅ **Order preservation** - Elements stay in the correct order after reimport
3. ✅ **Perfect round-trip** - Export → Import → Export produces identical output

## What Was Fixed

### 1. Importer Field Names (Critical for Ordering) ✅

**Problem**: The importer was using incorrect field names, causing the "out of order" issue you experienced.

**Fix**:
```python
# Before (WRONG):
ve_asset = {
    'id': current_id,              # ❌
    'parentId': parent_id,         # ❌
    'orderInDocument': len(...),   # ❌
}

# After (CORRECT):
ve_asset = {
    'm_Id': current_id,              # ✓
    'm_ParentId': parent_id,         # ✓
    'm_OrderInDocument': len(...),   # ✓
}
```

**Impact**: Elements now maintain their correct order and parent relationships after reimport.

---

### 2. Template Export ✅

**Problem**: Template instances (nested UXML files) were not being exported.

**Fixes**:
- Extract elements from both `m_VisualElementAssets` AND `m_TemplateAssets`
- Detect TemplateContainer by checking for `m_TemplateAlias` field
- Extract `templateId` from binding data and export as `template` attribute

**Result**:
```xml
<!-- Now exports template references! -->
<ui:TemplateContainer class="base-template-grow"
                      template="FigmaBaseToolTabbedTemplate"/>
<ui:TemplateContainer class="quick-action-buttons-template-layout"
                      template="QuickActionMenuButtons"/>
```

---

### 3. Template Import ✅

**Problem**: Template references couldn't be imported.

**Fixes**:
- Parse `template="..."` attribute from UXML
- Separate TemplateContainer elements into `m_TemplateAssets` array
- Store `m_TemplateAlias` for template reconstruction

**Result**: You can now modify which template is used and reimport.

---

## How To Use

### Viewing Nested UXML Files

**Export a VTA:**
```python
from fm_skin_builder.core.uxml.uxml_exporter import UXMLExporter
from pathlib import Path

exporter = UXMLExporter()
doc = exporter.export_visual_tree_asset(vta_data)
exporter.write_uxml(doc, Path("output.uxml"))
```

**Check the output for template references:**
```xml
<ui:TemplateContainer template="FigmaBaseToolTabbedTemplate"/>
```

This shows you which nested UXML file is being used!

---

### Moving Templates Around

**Example: Change which template is used**

**Before:**
```xml
<ui:TemplateContainer name="NonPhoneLayout"
                      template="FigmaBaseToolTabbedTemplate"
                      class="base-template-grow"/>
```

**After (use a different template):**
```xml
<ui:TemplateContainer name="NonPhoneLayout"
                      template="AlternativeLayoutTemplate"
                      class="base-template-grow"/>
```

**Then reimport:**
```python
from fm_skin_builder.core.uxml.uxml_importer import UXMLImporter

importer = UXMLImporter()
doc = importer.import_uxml(Path("output.uxml"))
vta_structure = importer.build_visual_tree_asset(doc)
```

The template reference will be updated!

---

### Moving Template Instances in Hierarchy

You can also move TemplateContainer elements to different parents by editing the UXML structure:

**Before:**
```xml
<ui:BindableSwitchElement>
  <ui:TemplateContainer template="FigmaBaseToolTabbedTemplate"/>
</ui:BindableSwitchElement>
```

**After (moved to a different parent):**
```xml
<ui:BindingRoot>
  <ui:TemplateContainer template="FigmaBaseToolTabbedTemplate"/>
</ui:BindingRoot>
```

Order is preserved based on document structure!

---

## Real Example: CalendarTool

**Exported UXML:**
```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements" ...>
  <ui:BindingRoot class="base-template-grow calendar-button-group">
    <ui:BindingVariables class="base-template-grow">
      <ui:BindingRemapper class="base-template-grow calender-button-group"
                          binding-mappings="yearindex=Year.PropertyValue;team=Human.Team">
        <ui:BindableSwitchElement class="base-template-grow"
                                   data-binding="config.ShowPhonePanels">
          <!-- ✓ Template instances visible! -->
          <ui:TemplateContainer class="base-template-grow"
                                template="FigmaBaseToolTabbedTemplate"/>
          <ui:TemplateContainer class="base-template-grow"
                                template="FigmaBaseToolTabbedTemplate"/>
        </ui:BindableSwitchElement>
        <ui:TemplateContainer class="quick-action-buttons-template-layout"
                              template="QuickActionMenuButtons"/>
      </ui:BindingRemapper>
    </ui:BindingVariables>
  </ui:BindingRoot>
</ui:UXML>
```

You can now:
- ✅ See that CalendarTool uses 3 template instances
- ✅ See which templates are used (FigmaBaseToolTabbedTemplate, QuickActionMenuButtons)
- ✅ Move template instances around in the hierarchy
- ✅ Change which template is used by editing the `template` attribute

---

## Round-Trip Test Results

**Test**: Export → Import → Export

**Result**: ✅ **Perfect Match**

```
Export 1 size: 980 chars
Import: 4 visual elements, 3 template elements
Export 2 size: 980 chars

✓ Exports are IDENTICAL
```

**What's preserved**:
- ✅ Element order (m_OrderInDocument)
- ✅ Parent-child relationships (m_ParentId)
- ✅ Element IDs (m_Id)
- ✅ Template references
- ✅ Data bindings
- ✅ Class names
- ✅ All attributes

---

## Additional Unity 2021+ Fixes

Also updated the importer to match Unity 2021+ format:
- ✅ Store strings directly (not as string table indices)
- ✅ Use `m_FullTypeName` instead of `m_TypeName`
- ✅ Properly reconstruct full type names with namespaces
- ✅ Handle both Unity and SI.Bindable namespaces

---

## Testing

Tested with real FM26 bundle (`ui-panelids-uxml_assets_all.bundle`):
- ✅ CalendarTool: 4 elements + 3 templates
- ✅ Perfect round-trip match
- ✅ All template references preserved
- ✅ All bindings preserved
- ✅ Order maintained

---

## Commits

**fc68c98**: "fix: correct field names and add template support for import/export"
- Importer field name fixes
- Template export from m_TemplateAssets
- Template import with template attribute
- Round-trip verification

**Branch**: `claude/uxml-import-export-pipeline-011F7NNuAubpKgmoqPW6SgF2`

---

## What You Can Do Now

### 1. View Nested UXML Structure
Export any VTA and see which nested UXML files it uses.

### 2. Move Templates Around
Change the `template` attribute to use different templates.

### 3. Reorganize UI Hierarchy
Move TemplateContainer elements to different parents by editing UXML structure.

### 4. Confident Reimport
The order and structure will be preserved exactly as you edited it.

---

**Status**: ✅ ALL FIXES COMPLETE AND TESTED

Your UXML pipeline now supports full template editing and maintains perfect order on round-trips!
