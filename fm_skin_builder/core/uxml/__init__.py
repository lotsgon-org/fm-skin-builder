"""
UXML Import/Export Pipeline

This module provides functionality to:
1. Export VisualTreeAsset objects to editable UXML text files
2. Import edited UXML text back into VisualTreeAsset objects
3. Handle inline StyleSheet serialization/deserialization
4. Safely inject modified assets into Unity bundles

The pipeline enables offline editing of FM26's UI Toolkit interfaces.
"""

from .uxml_ast import (
    UXMLElement,
    UXMLAttribute,
    UXMLDocument,
    UXMLTemplate,
)
from .uxml_exporter import UXMLExporter
from .uxml_importer import UXMLImporter
from .style_parser import StyleParser
from .style_serializer import StyleSerializer

__all__ = [
    "UXMLElement",
    "UXMLAttribute",
    "UXMLDocument",
    "UXMLTemplate",
    "UXMLExporter",
    "UXMLImporter",
    "StyleParser",
    "StyleSerializer",
]
