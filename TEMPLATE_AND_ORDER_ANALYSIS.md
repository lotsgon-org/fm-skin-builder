# Template Handling and Order Preservation Analysis

## Issues Found

### 1. Template References Not Exported ❌

**Problem**: Template instances (TemplateContainer elements with `templateId`) are NOT being exported with their template references.

**Evidence from CalendarTool**:
- Template reference exists: RID 1004 has `templateId: 'FigmaBaseToolTabbedTemplate'`
- But this is NOT exported in the UXML

**What's Missing**:
```xml
<!-- Current export (missing template reference) -->
<ui:TemplateContainer name="NonPhoneLayout" class="..."/>

<!-- Should export as -->
<ui:TemplateContainer name="NonPhoneLayout"
                      template="FigmaBaseToolTabbedTemplate"
                      class="..."/>
```

**Impact**:
- Cannot see which templates are used where
- Cannot move templates around (change which template is used)
- Nested UXML files are invisible in exports

---

### 2. Order Preservation Issues in Importer ⚠️

**Problem**: Field names in importer don't match Unity's actual field names.

**Code from uxml_importer.py:134-141**:
```python
ve_asset = {
    'id': current_id,              # ❌ Should be 'm_Id'
    'parentId': parent_id,          # ❌ Should be 'm_ParentId'
    'orderInDocument': len(visual_elements),  # ❌ Should be 'm_OrderInDocument'
    'm_TypeName': elem.element_type,
    ...
}
```

**Unity's Actual Fields**:
- `m_Id` (not `id`)
- `m_ParentId` (not `parentId`)
- `m_OrderInDocument` (not `orderInDocument`)

**Impact**:
- Reimported elements may have incorrect IDs and parent relationships
- Order may not be preserved correctly
- This is likely the cause of "screen sections all out of order" mentioned by user

---

### 3. Template Import Not Implemented ❌

**Problem**: Even if we export template references, the importer doesn't handle them.

**Missing**: Code to:
1. Parse `template="TemplateName"` attributes from UXML
2. Look up template in `m_TemplateAssets`
3. Set `m_Template` PPtr reference on element
4. Create UxmlSerializedData with `templateId` field

---

## Test Case: CalendarTool

### Current Behavior

**Export Output**:
```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements" ...>
  <ui:BindingRoot class="base-template-grow calendar-button-group">
    <ui:BindingVariables class="base-template-grow">
      <ui:BindingRemapper class="base-template-grow calender-button-group"
                          binding-mappings="yearindex=Year.PropertyValue;team=Human.Team">
        <ui:BindableSwitchElement class="base-template-grow"
                                   data-binding="config.ShowPhonePanels"/>
      </ui:BindingRemapper>
    </ui:BindingVariables>
  </ui:BindingRoot>
</ui:UXML>
```

**Missing**:
- Template declarations at top (`<Template name="..." src="..."/>`)
- Template references on TemplateContainer elements

### Expected Behavior

Looking at Unity's UXML format and the binding data we found:

**Should Export**:
```xml
<ui:UXML xmlns:ui="UnityEngine.UIElements" ...>
  <!-- Template declarations -->
  <Template name="FigmaBaseToolTabbedTemplate" src="path/to/template.uxml"/>
  <Template name="PhoneLayout" src="path/to/phone.uxml"/>
  <Template name="QuickActions" src="path/to/quickactions.uxml"/>

  <ui:BindingRoot class="base-template-grow calendar-button-group">
    <ui:BindingVariables class="base-template-grow">
      <ui:BindingRemapper class="base-template-grow calender-button-group"
                          binding-mappings="yearindex=Year.PropertyValue;team=Human.Team">
        <ui:BindableSwitchElement class="base-template-grow"
                                   data-binding="config.ShowPhonePanels">

          <!-- Template instances (these are nested UXML files) -->
          <ui:TemplateContainer name="NonPhoneLayout"
                                template="FigmaBaseToolTabbedTemplate"
                                class="..."/>
          <ui:TemplateContainer name="PhoneLayout"
                                template="FigmaBaseToolTabbedTemplate"
                                class="..."/>
          <ui:TemplateContainer name="QuickActions"
                                template="QuickActions"
                                class="..."/>
        </ui:BindableSwitchElement>
      </ui:BindingRemapper>
    </ui:BindingVariables>
  </ui:BindingRoot>
</ui:UXML>
```

---

## Detailed Analysis

### Template Storage in Unity

Unity stores templates in two places:

**1. VTA Level (m_TemplateAssets)**:
```python
# Array of template references
template_assets = [
    {
        'm_Name': '',  # Often empty
        'm_FileID': 0,
        'm_PathID': 0,
        'guid': '...',
    },
    ...
]
```

**2. Element Level (UxmlSerializedData)**:
```python
# For TemplateContainer elements
{
    'uxmlAssetId': -1738418621,  # Maps to element ID
    'templateId': 'FigmaBaseToolTabbedTemplate',  # The template name!
    'template': PPtr(...),  # Pointer to template asset
    ...
}
```

### How to Fix

**Exporter Changes Needed**:

1. **Extract templateId from binding data**:
```python
# In _extract_binding_attributes()
template_id = getattr(ref_data, 'templateId', None)
if template_id and template_id.strip():
    attributes.append(UXMLAttribute(
        name="template",
        value=template_id
    ))
```

2. **Export Template declarations**:
```python
# Already done at line 575-579, but need to fix template names
# Current code exports templates with empty names
```

**Importer Changes Needed**:

1. **Fix field names**:
```python
ve_asset = {
    'm_Id': current_id,              # ✓ Fixed
    'm_ParentId': parent_id,         # ✓ Fixed
    'm_OrderInDocument': len(visual_elements),  # ✓ Fixed
    ...
}
```

2. **Handle template attribute**:
```python
elif attr.name == 'template':
    # Store template reference
    ve_asset['templateId'] = attr.value
    # Need to look up template in m_TemplateAssets
```

3. **Rebuild references with templateId**:
```python
# When building VTA, need to create UxmlSerializedData entries
# with templateId for TemplateContainer elements
```

---

## Summary for User

### Question 1: "Do we handle custom UXML templates that are nested within elements?"

**Answer**: ❌ **Not currently**.

- Template references exist in the data (e.g., `templateId: 'FigmaBaseToolTabbedTemplate'`)
- But we're NOT exporting them in the UXML
- You can't see which templates are used where
- You can't move templates around

**Needs**: Exporter enhancement to extract `templateId` and export as `template="..."` attribute.

### Question 2: "Are we keeping all references and the order intact on reimport?"

**Answer**: ⚠️ **Partially, with bugs**.

- Order IS being tracked (`orderInDocument` set to `len(visual_elements)`)
- But field names are WRONG (missing `m_` prefix)
- This could cause the "out of order" issue you experienced

**Needs**: Importer fix to use correct field names (`m_Id`, `m_ParentId`, `m_OrderInDocument`).

---

## Priority Fixes Needed

1. **HIGH**: Fix importer field names (`id` → `m_Id`, etc.)
2. **HIGH**: Export template references (`templateId` → `template="..."` attribute)
3. **MEDIUM**: Import template references (parse `template` attribute, rebuild refs)
4. **MEDIUM**: Fix template declarations (get actual template names)
5. **LOW**: Support moving templates around (change which template is used where)

---

## Testing Needed

After fixes:

1. Export a VTA with templates → Verify template declarations and references appear
2. Modify template reference → Reimport → Verify change took effect
3. Export → Import → Export → Verify order preserved and output identical
4. Check element IDs, parent IDs, and order match original after round-trip
