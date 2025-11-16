#!/usr/bin/env python3
"""
Detailed VTA structure examination.
"""
import sys
sys.path.insert(0, '/home/user/fm-skin-builder')

import UnityPy
from pathlib import Path

# Load the test bundle
env = UnityPy.load("test_bundles/ui-panelids-uxml_assets_all.bundle")

# Find VTAs
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

# Find a slightly larger one with variety
medium_vtas = [(n, d, o) for n, d, o in vta_objects if 10 <= len(d.m_VisualElementAssets) <= 20]
if medium_vtas:
    name, data, obj = medium_vtas[0]
    print(f"=== Examining '{name}' (has {len(data.m_VisualElementAssets)} elements) ===\n")

    print("=== All Visual Elements ===\n")
    for i, elem in enumerate(data.m_VisualElementAssets):
        print(f"Element {i}:")
        print(f"  m_FullTypeName: {elem.m_FullTypeName}")
        print(f"  m_Id: {elem.m_Id}")
        print(f"  m_ParentId: {elem.m_ParentId}")
        print(f"  m_OrderInDocument: {elem.m_OrderInDocument}")
        print(f"  m_Name: '{elem.m_Name}'")
        print(f"  m_Classes: {elem.m_Classes}")
        print(f"  m_Properties: {len(elem.m_Properties)} properties")

        # Show properties
        if elem.m_Properties:
            for j, prop in enumerate(elem.m_Properties[:3]):  # First 3 props
                print(f"    Property {j}:")
                for attr in sorted(dir(prop)):
                    if not attr.startswith('_') and not callable(getattr(prop, attr)):
                        val = getattr(prop, attr)
                        if not isinstance(val, (list, dict)) or len(str(val)) < 100:
                            print(f"      {attr}: {val}")

        print()

print("\n=== Done ===")
