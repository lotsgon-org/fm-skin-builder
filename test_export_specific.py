#!/usr/bin/env python3
"""
Export specific VTAs with Unity standard elements.
"""
import sys
sys.path.insert(0, '/home/user/fm-skin-builder')

import UnityPy
from pathlib import Path
from fm_skin_builder.core.uxml import UXMLExporter

# Load bundle
env = UnityPy.load("test_bundles/ui-panelids-uxml_assets_all.bundle")

# Find specific VTAs
targets = ["MatchFocusRadioButtonDebugTest", "NationSelectionButtonSmall", "ClubSelectionButton"]

output_dir = Path("test_uxml_output")
output_dir.mkdir(exist_ok=True)

exporter = UXMLExporter()

for obj in env.objects:
    if obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            if hasattr(data, "m_VisualElementAssets"):
                name = getattr(data, "m_Name", "")
                if name in targets:
                    print(f"\n{'='*60}")
                    print(f"Exporting '{name}'")
                    print(f"{'='*60}")

                    output_path = output_dir / f"{name}.uxml"
                    doc = exporter.export_visual_tree_asset(data, output_path)

                    # Show full output
                    content = output_path.read_text()
                    print(content)

                    targets.remove(name)
                    if not targets:
                        break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

print("\n=== Done ===")
