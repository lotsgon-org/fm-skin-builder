"""
UXML Exporter - VisualTreeAsset → UXML Text

Exports Unity's VisualTreeAsset objects to human-readable UXML text files.
Handles hierarchy reconstruction, attribute extraction, and inline style serialization.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

from .uxml_ast import (
    UXMLDocument,
    UXMLElement,
    UXMLAttribute,
    UXMLTemplate,
)
from .style_parser import StyleParser
from ..logger import get_logger

log = get_logger(__name__)


class UXMLExporter:
    """Exports VisualTreeAsset objects to UXML text."""

    def __init__(self):
        """Initialize the UXML exporter."""
        self.style_parser = StyleParser()

    def export_visual_tree_asset(
        self,
        vta_data: Any,
        output_path: Optional[Path] = None
    ) -> UXMLDocument:
        """
        Export a VisualTreeAsset to a UXML document.

        Args:
            vta_data: Unity VisualTreeAsset object from UnityPy
            output_path: Optional path to write UXML file

        Returns:
            UXMLDocument object
        """
        asset_name = getattr(vta_data, "m_Name", "Unknown")
        log.info(f"Exporting VisualTreeAsset: {asset_name}")

        # Create UXML document
        doc = UXMLDocument(asset_name=asset_name)

        # Extract templates
        doc.templates = self._extract_templates(vta_data)

        # Extract visual element hierarchy
        doc.root = self._extract_visual_tree(vta_data)

        # Extract inline styles (from associated StyleSheet)
        inline_stylesheet = self._get_inline_stylesheet(vta_data)
        if inline_stylesheet:
            doc.inline_styles = self.style_parser.parse_stylesheet(inline_stylesheet)

        # Write to file if path provided
        if output_path:
            self.write_uxml(doc, output_path)

        return doc

    def _extract_templates(self, vta_data: Any) -> List[UXMLTemplate]:
        """
        Extract template references from VisualTreeAsset.

        Args:
            vta_data: Unity VisualTreeAsset object

        Returns:
            List of UXMLTemplate objects
        """
        templates = []

        # Unity stores template references in m_TemplateAssets
        template_assets = getattr(vta_data, "m_TemplateAssets", [])

        for template_ref in template_assets:
            # Template reference contains PPtr to another VisualTreeAsset
            # In bundles, this is stored as FileID/PathID
            name = getattr(template_ref, "m_Name", None)
            guid = getattr(template_ref, "guid", None)
            file_id = getattr(template_ref, "m_FileID", None)

            if name:
                templates.append(UXMLTemplate(
                    name=name,
                    src=f"{name}.uxml",  # Conventional path
                    guid=guid,
                    file_id=file_id
                ))

        return templates

    def _extract_visual_tree(self, vta_data: Any) -> Optional[UXMLElement]:
        """
        Extract visual element hierarchy from VisualTreeAsset.

        Args:
            vta_data: Unity VisualTreeAsset object

        Returns:
            Root UXMLElement or None
        """
        # Unity stores visual elements in m_VisualElementAssets
        visual_elements = getattr(vta_data, "m_VisualElementAssets", [])
        if not visual_elements:
            log.warning("No visual elements found in VisualTreeAsset")
            return None

        # Build element map
        elements_by_id: Dict[int, UXMLElement] = {}

        # First pass: create all elements
        for ve_asset in visual_elements:
            element = self._create_element_from_asset(ve_asset, vta_data)
            if element.id is not None:
                elements_by_id[element.id] = element

        # Second pass: build hierarchy
        for ve_asset in visual_elements:
            elem_id = getattr(ve_asset, "id", None)
            parent_id = getattr(ve_asset, "parentId", None)

            if elem_id is not None and parent_id is not None and parent_id != -1:
                # This element has a parent
                if elem_id in elements_by_id and parent_id in elements_by_id:
                    parent = elements_by_id[parent_id]
                    child = elements_by_id[elem_id]
                    parent.children.append(child)

        # Find root element (no parent or parent = -1)
        root = None
        for ve_asset in visual_elements:
            parent_id = getattr(ve_asset, "parentId", None)
            elem_id = getattr(ve_asset, "id", None)

            if parent_id is None or parent_id == -1:
                if elem_id is not None and elem_id in elements_by_id:
                    root = elements_by_id[elem_id]
                    break

        # Sort children by orderInDocument
        self._sort_children_recursive(root)

        return root

    def _create_element_from_asset(
        self,
        ve_asset: Any,
        vta_data: Any
    ) -> UXMLElement:
        """
        Create a UXMLElement from a VisualElementAsset.

        Args:
            ve_asset: Unity VisualElementAsset object
            vta_data: Parent VisualTreeAsset (for string lookups)

        Returns:
            UXMLElement object
        """
        # Get element type
        type_name = self._get_element_type_name(ve_asset)

        # Create element
        element = UXMLElement(
            element_type=type_name,
            id=getattr(ve_asset, "id", None),
            parent_id=getattr(ve_asset, "parentId", None),
            order_in_document=getattr(ve_asset, "orderInDocument", None)
        )

        # Extract attributes from UxmlTraits
        attributes = self._extract_attributes(ve_asset, vta_data)
        element.attributes = attributes

        # Extract text content (for Label, Button, etc.)
        element.text = self._extract_text_content(ve_asset, vta_data)

        # Extract template reference if this is a Template instance
        template_ref = getattr(ve_asset, "m_Template", None)
        if template_ref:
            element.template_asset = getattr(template_ref, "m_Name", None)

        return element

    def _get_element_type_name(self, ve_asset: Any) -> str:
        """
        Get the element type name from a VisualElementAsset.

        Args:
            ve_asset: Unity VisualElementAsset object

        Returns:
            Element type name (e.g., "VisualElement", "Label", "Button")
        """
        # Unity stores the type name in various ways
        # Try m_Name first (for custom elements)
        type_name = getattr(ve_asset, "m_TypeName", None)

        if not type_name:
            # Fallback: check the type of the object itself
            # This requires examining the Unity class structure
            # For now, default to VisualElement
            type_name = "VisualElement"

        return type_name

    def _extract_attributes(
        self,
        ve_asset: Any,
        vta_data: Any
    ) -> List[UXMLAttribute]:
        """
        Extract UXML attributes from VisualElementAsset.

        Args:
            ve_asset: Unity VisualElementAsset object
            vta_data: Parent VisualTreeAsset

        Returns:
            List of UXMLAttribute objects
        """
        attributes = []

        # Get string table from VisualTreeAsset
        string_table = getattr(vta_data, "m_Strings", [])

        # Extract common attributes

        # 1. name attribute
        name_index = getattr(ve_asset, "m_Name", None)
        if name_index is not None and 0 <= name_index < len(string_table):
            name_value = string_table[name_index]
            if name_value:
                attributes.append(UXMLAttribute(name="name", value=name_value))

        # 2. class list
        classes = getattr(ve_asset, "m_Classes", [])
        if classes:
            class_names = []
            for class_index in classes:
                if 0 <= class_index < len(string_table):
                    class_names.append(string_table[class_index])

            if class_names:
                attributes.append(UXMLAttribute(
                    name="class",
                    value=" ".join(class_names)
                ))

        # 3. Extract other UxmlTraits
        # Unity stores these in various fields depending on the element type
        # For now, we'll extract the most common ones

        # Style classes (in addition to m_Classes)
        style_classes = getattr(ve_asset, "m_ClassList", [])
        if style_classes and not classes:
            # Convert indices to names
            class_names = []
            for class_index in style_classes:
                if 0 <= class_index < len(string_table):
                    class_names.append(string_table[class_index])

            if class_names:
                attributes.append(UXMLAttribute(
                    name="class",
                    value=" ".join(class_names)
                ))

        # Inline style (if present)
        # Note: Most inline styles are in the StyleSheet, not here
        inline_style = getattr(ve_asset, "m_Style", None)
        if inline_style:
            # This would need proper style parsing
            # For now, skip - styles are typically in separate StyleSheet
            pass

        return attributes

    def _extract_text_content(
        self,
        ve_asset: Any,
        vta_data: Any
    ) -> Optional[str]:
        """
        Extract text content from element (for Label, Button, etc.).

        Args:
            ve_asset: Unity VisualElementAsset object
            vta_data: Parent VisualTreeAsset

        Returns:
            Text content or None
        """
        string_table = getattr(vta_data, "m_Strings", [])

        # Check for text field
        text_index = getattr(ve_asset, "m_Text", None)
        if text_index is not None and 0 <= text_index < len(string_table):
            return string_table[text_index]

        return None

    def _sort_children_recursive(self, element: Optional[UXMLElement]) -> None:
        """
        Sort children by orderInDocument recursively.

        Args:
            element: UXMLElement to process
        """
        if not element:
            return

        # Sort children by orderInDocument
        element.children.sort(key=lambda e: e.order_in_document or 0)

        # Recursively sort grandchildren
        for child in element.children:
            self._sort_children_recursive(child)

    def _get_inline_stylesheet(self, vta_data: Any) -> Optional[Any]:
        """
        Get the inline StyleSheet associated with a VisualTreeAsset.

        Args:
            vta_data: Unity VisualTreeAsset object

        Returns:
            StyleSheet object or None
        """
        # Unity stores inline styles in m_InlineSheet
        inline_sheet = getattr(vta_data, "m_InlineSheet", None)

        if inline_sheet:
            # This might be a PPtr reference or direct object
            # Try to read it
            try:
                if hasattr(inline_sheet, "read"):
                    return inline_sheet.read()
                else:
                    return inline_sheet
            except Exception as e:
                log.warning(f"Failed to read inline stylesheet: {e}")
                return None

        return None

    def write_uxml(self, doc: UXMLDocument, output_path: Path) -> None:
        """
        Write UXML document to file.

        Args:
            doc: UXMLDocument to write
            output_path: Path to output file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build XML tree
        root_elem = ET.Element("ui:UXML")
        root_elem.set("xmlns:ui", "UnityEngine.UIElements")
        root_elem.set("xmlns:uie", "UnityEditor.UIElements")

        # Add templates
        for template in doc.templates:
            template_elem = ET.SubElement(root_elem, "Template")
            template_elem.set("name", template.name)
            template_elem.set("src", template.src)

        # Add visual tree
        if doc.root:
            self._build_xml_element(doc.root, root_elem)

        # Add inline styles as comment (if present)
        if doc.inline_styles:
            style_comment = ET.Comment(f"\n Inline Styles:\n{doc.inline_styles}\n")
            root_elem.append(style_comment)

        # Convert to pretty-printed XML
        xml_str = ET.tostring(root_elem, encoding='unicode')
        try:
            dom = minidom.parseString(xml_str)
            pretty_xml = dom.toprettyxml(indent="  ")

            # Remove extra blank lines
            lines = [line for line in pretty_xml.split('\n') if line.strip()]
            pretty_xml = '\n'.join(lines)

        except Exception as e:
            log.warning(f"Failed to pretty-print XML: {e}")
            pretty_xml = xml_str

        # Write to file
        output_path.write_text(pretty_xml, encoding='utf-8')
        log.info(f"Wrote UXML to {output_path}")

    def _build_xml_element(
        self,
        element: UXMLElement,
        parent_xml: ET.Element
    ) -> None:
        """
        Recursively build XML elements.

        Args:
            element: UXMLElement to convert
            parent_xml: Parent XML element
        """
        # Create XML element with namespace prefix
        xml_elem = ET.SubElement(parent_xml, f"ui:{element.element_type}")

        # Add attributes
        for attr in element.attributes:
            xml_elem.set(attr.name, attr.value)

        # Add text content
        if element.text:
            xml_elem.text = element.text

        # Add children recursively
        for child in element.children:
            self._build_xml_element(child, xml_elem)
