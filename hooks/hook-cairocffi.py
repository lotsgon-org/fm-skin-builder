"""
PyInstaller hook for bundling Cairo library with the application.
This ensures cairosvg/cairocffi can find the native Cairo library.
"""
import os
import sys
from pathlib import Path

# Collect data files
datas = []

# Collect binaries - we need to find and bundle the Cairo library AND its dependencies
binaries = []

def find_cairo_and_dependencies():
    """Locate Cairo library and all its dependencies on the system."""
    platform = sys.platform
    found_libs = []

    if platform == 'win32':
        # Windows: Cairo and its complete dependency chain
        lib_names = [
            # Core Cairo
            'libcairo-2.dll',
            'cairo-2.dll',

            # Image and graphics libraries
            'libpng16-16.dll',
            'libpixman-1-0.dll',

            # Font libraries
            'libfreetype-6.dll',
            'libfontconfig-1.dll',
            'libharfbuzz-0.dll',
            'libgraphite2.dll',

            # Compression
            'zlib1.dll',
            'libbz2-1.dll',
            'libbrotlidec.dll',
            'libbrotlicommon.dll',

            # XML and text processing
            'libexpat-1.dll',

            # Character encoding
            'libiconv-2.dll',
            'libintl-8.dll',

            # GLib and dependencies
            'libglib-2.0-0.dll',
            'libpcre2-8-0.dll',
            'libffi-8.dll',

            # Runtime libraries
            'libgcc_s_seh-1.dll',
            'libstdc++-6.dll',
            'libwinpthread-1.dll',
        ]

        search_paths = [
            Path('C:/msys64/mingw64/bin'),       # MSYS2 (default location)
            Path(sys.prefix) / 'DLLs',           # Python DLLs directory
            Path(sys.prefix) / 'Library' / 'bin', # Conda
            Path(sys.prefix) / 'bin',
            Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'GTK3-Runtime' / 'bin',
        ]

    elif platform == 'darwin':
        # macOS: Cairo and dependencies
        lib_names = [
            'libcairo.2.dylib',
            'libpng16.16.dylib',
            'libfreetype.6.dylib',
            'libfontconfig.1.dylib',
            'libpixman-1.0.dylib',
        ]

        search_paths = [
            Path('/opt/homebrew/lib'),  # ARM Homebrew
            Path('/usr/local/lib'),      # Intel Homebrew
            Path(sys.prefix) / 'lib',
        ]

    else:
        # Linux: Cairo and dependencies
        lib_names = [
            'libcairo.so.2',
            'libpng16.so.16',
            'libfreetype.so.6',
            'libfontconfig.so.1',
            'libpixman-1.so.0',
        ]

        search_paths = [
            Path('/usr/lib/x86_64-linux-gnu'),
            Path('/usr/lib'),
            Path('/usr/local/lib'),
            Path(sys.prefix) / 'lib',
        ]

    # Search for libraries
    for search_path in search_paths:
        if not search_path.exists():
            continue

        for lib_name in lib_names:
            lib_path = search_path / lib_name
            if lib_path.exists() and str(lib_path) not in found_libs:
                found_libs.append(str(lib_path))
                print(f"[hook-cairocffi] Found: {lib_path}")

    return found_libs

try:
    libs = find_cairo_and_dependencies()
    if libs:
        # Bundle all found libraries
        for lib_path in libs:
            binaries.append((lib_path, '.'))
        print(f"[hook-cairocffi] Successfully bundled {len(libs)} Cairo-related libraries")
    else:
        print("[hook-cairocffi] WARNING: Could not locate Cairo library on system")
        print("[hook-cairocffi] Application may fail at runtime if Cairo is not installed")
except Exception as e:
    print(f"[hook-cairocffi] Error while searching for Cairo: {e}")
    import traceback
    traceback.print_exc()

