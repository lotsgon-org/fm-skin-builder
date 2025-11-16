#!/usr/bin/env python3
"""
Test script to examine VTA structure and export UXML.
"""
import sys
sys.path.insert(0, '/home/user/fm-skin-builder')

import UnityPy
from pathlib import Path

# Load the test bundle
env = UnityPy.load("test_bundles/ui-panelids-uxml_assets_all.bundle")

print("=== Finding VisualTreeAssets ===\n")

vta_objects = []
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            if hasattr(data, "m_VisualElementAssets"):
                name = getattr(data, "m_Name", "Unnamed")
                vta_objects.append((name, data, obj))
        except:
            pass

print(f"Found {len(vta_objects)} VTAs\n")

# Pick a simple one to examine
simple_vtas = [(n, d, o) for n, d, o in vta_objects if len(d.m_VisualElementAssets) < 15]
if simple_vtas:
    name, data, obj = simple_vtas[0]
    print(f"=== Examining '{name}' (has {len(data.m_VisualElementAssets)} elements) ===\n")

    print("VTA Fields:")
    print(f"  m_Name: {data.m_Name}")
    print(f"  m_VisualElementAssets: {len(data.m_VisualElementAssets)} elements")
    print(f"  m_TemplateAssets: {len(data.m_TemplateAssets) if hasattr(data, 'm_TemplateAssets') else 'N/A'}")
    print(f"  m_AssetEntries: {len(data.m_AssetEntries) if hasattr(data, 'm_AssetEntries') else 'N/A'}")
    print(f"  m_UxmlObjectEntries: {len(data.m_UxmlObjectEntries) if hasattr(data, 'm_UxmlObjectEntries') else 'N/A'}")

    print("\n=== First Visual Element ===")
    if data.m_VisualElementAssets:
        elem = data.m_VisualElementAssets[0]
        print(f"Type: {type(elem).__name__}")
        print(f"Fields:")
        for attr in sorted(dir(elem)):
            if not attr.startswith('_') and not callable(getattr(elem, attr)):
                val = getattr(elem, attr)
                # Show value but truncate if too long
                if isinstance(val, (list, tuple)) and len(val) > 5:
                    print(f"  {attr}: [{len(val)} items]")
                elif isinstance(val, str) and len(val) > 50:
                    print(f"  {attr}: {val[:50]}...")
                else:
                    print(f"  {attr}: {val}")

    # Check for asset entries (these map to element types)
    if hasattr(data, 'm_AssetEntries') and data.m_AssetEntries:
        print(f"\n=== Asset Entries (Element Type Definitions) ===")
        for i, entry in enumerate(data.m_AssetEntries[:5]):  # First 5
            print(f"\nEntry {i}:")
            for attr in sorted(dir(entry)):
                if not attr.startswith('_') and not callable(getattr(entry, attr)):
                    val = getattr(entry, attr)
                    if isinstance(val, str) and len(val) > 50:
                        print(f"  {attr}: {val[:50]}...")
                    else:
                        print(f"  {attr}: {val}")

print("\n=== Done ===")
