#!/usr/bin/env python3
"""
Comprehensive test with real FM26 bundle data.
"""
import sys
sys.path.insert(0, '/home/user/fm-skin-builder')

import UnityPy
from pathlib import Path
from fm_skin_builder.core.uxml import UXMLExporter, UXMLImporter

print("="*80)
print("UXML Export/Import Comprehensive Test")
print("="*80)

# Load bundle
env = UnityPy.load("test_bundles/ui-panelids-uxml_assets_all.bundle")

# Find a variety of VTAs to test
test_cases = [
    ("Simple VTA", lambda d: 3 <= len(d.m_VisualElementAssets) <= 6),
    ("Medium VTA", lambda d: 10 <= len(d.m_VisualElementAssets) <= 15),
    ("Complex VTA", lambda d: 20 <= len(d.m_VisualElementAssets) <= 30),
]

output_dir = Path("test_uxml_comprehensive")
output_dir.mkdir(exist_ok=True)

exporter = UXMLExporter()
importer = UXMLImporter()

total_tests = 0
passed_tests = 0

for test_name, condition in test_cases:
    print(f"\n{test_name} Test:")
    print("-" * 40)

    # Find matching VTA
    found = False
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour":
            try:
                data = obj.read()
                if hasattr(data, "m_VisualElementAssets") and condition(data):
                    name = getattr(data, "m_Name", "Unknown")
                    elements = data.m_VisualElementAssets

                    print(f"Testing: {name} ({len(elements)} elements)")
                    total_tests += 1

                    # Export
                    output_path = output_dir / f"{name}.uxml"
                    try:
                        doc = exporter.export_visual_tree_asset(data, output_path)

                        # Verify export
                        content = output_path.read_text()

                        # Check UXML structure
                        checks = {
                            "Has UXML root": '<ui:UXML' in content,
                            "Has namespace": 'xmlns:ui="UnityEngine.UIElements"' in content,
                            "Has elements": len(content.split('\n')) > 3,
                            "Valid XML structure": content.count('<') == content.count('>'),
                            "Has closing tag": '</ui:UXML>' in content,
                        }

                        all_passed = all(checks.values())

                        if all_passed:
                            print(f"  ✓ Export successful")
                            passed_tests += 1

                            # Test round-trip
                            try:
                                reimported = importer.import_uxml(output_path)
                                if reimported.root is not None:
                                    print(f"  ✓ Round-trip successful")
                                else:
                                    print(f"  ✗ Round-trip failed: no root element")
                            except Exception as e:
                                print(f"  ✗ Round-trip failed: {e}")

                            # Show sample
                            lines = content.split('\n')[:15]
                            print(f"  Sample output:")
                            for line in lines:
                                print(f"    {line}")

                        else:
                            print(f"  ✗ Export validation failed:")
                            for check, result in checks.items():
                                if not result:
                                    print(f"    - {check}: FAILED")

                    except Exception as e:
                        print(f"  ✗ Export failed: {e}")
                        import traceback
                        traceback.print_exc()

                    found = True
                    break
            except:
                pass

        if found:
            break

    if not found:
        print(f"  ⚠ No matching VTA found for {test_name}")

print("\n" + "="*80)
print(f"Results: {passed_tests}/{total_tests} tests passed")
print("="*80)

if passed_tests == total_tests:
    print("✓ All tests passed!")
    sys.exit(0)
else:
    print("✗ Some tests failed")
    sys.exit(1)
