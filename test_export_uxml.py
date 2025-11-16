#!/usr/bin/env python3
"""
Test UXML export with real bundle.
"""
import sys
sys.path.insert(0, '/home/user/fm-skin-builder')

import UnityPy
from pathlib import Path
from fm_skin_builder.core.uxml import UXMLExporter

# Load the test bundle
print("Loading bundle...")
env = UnityPy.load("test_bundles/ui-panelids-uxml_assets_all.bundle")

# Find VTAs
vta_list = []
for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            if hasattr(data, "m_VisualElementAssets"):
                name = getattr(data, "m_Name", "Unnamed")
                vta_list.append((name, data, obj))
        except:
            pass

print(f"Found {len(vta_list)} VTAs\n")

# Export a few simple ones
output_dir = Path("test_uxml_output")
output_dir.mkdir(exist_ok=True)

exporter = UXMLExporter()

# Export first 5 simple VTAs
simple_vtas = [(n, d, o) for n, d, o in vta_list if len(d.m_VisualElementAssets) < 15]
for i, (name, data, obj) in enumerate(simple_vtas[:5]):
    print(f"\nExporting '{name}' ({len(data.m_VisualElementAssets)} elements)...")
    try:
        output_path = output_dir / f"{name}.uxml"
        doc = exporter.export_visual_tree_asset(data, output_path)
        print(f"  ✓ Exported to {output_path}")

        # Show first few lines
        content = output_path.read_text()
        lines = content.split('\n')[:20]
        print("  First 20 lines:")
        for line in lines:
            print(f"    {line}")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n=== Done ===")
