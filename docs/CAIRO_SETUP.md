# Cairo Library Setup

The FM Skin Builder uses [CairoSVG](https://cairosvg.org/) for SVG processing in the asset catalogue feature. CairoSVG requires the native Cairo graphics library to be installed on your system.

## Why is this needed?

Cairo is a 2D graphics library that provides low-level rendering capabilities. When you build the application with PyInstaller, the Cairo native library needs to be:
1. Available on your system during the build
2. Bundled into the final executable

## Installation Instructions

### Windows

**Option 1: Download pre-built binaries (Recommended)**
```powershell
# Download Cairo for Windows
$url = "https://github.com/preshing/cairo-windows/releases/download/v1.17.2/cairo-windows-1.17.2.zip"
Invoke-WebRequest -Uri $url -OutFile cairo-windows.zip
Expand-Archive -Path cairo-windows.zip -DestinationPath cairo-windows

# Copy to Python DLLs directory (adjust path to your Python installation)
Copy-Item cairo-windows/cairo.dll $env:PYTHON_LOCATION/DLLs/libcairo-2.dll
```

**Option 2: Install via MSYS2**
```bash
pacman -S mingw-w64-x86_64-cairo
```

**Option 3: Install GTK3 Runtime**
Download and install [GTK3 Runtime for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)

### macOS

**Using Homebrew:**
```bash
brew install cairo
```

**Using MacPorts:**
```bash
sudo port install cairo
```

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y libcairo2 libcairo2-dev
```

### Linux (Fedora/RHEL)

```bash
sudo dnf install cairo cairo-devel
```

### Linux (Arch)

```bash
sudo pacman -S cairo
```

## Verifying Installation

After installing Cairo, you can verify it's available to Python:

```python
python -c "import cairocffi; print('Cairo found:', cairocffi.cairo_version_string())"
```

If this command runs without errors and prints a version number, Cairo is properly installed.

## Building the Application

Once Cairo is installed, you can build the backend:

```bash
# Using the build script (recommended)
./scripts/build_backend.sh

# Or manually with PyInstaller
python -m PyInstaller \
    --onefile \
    --name fm_skin_builder \
    --hidden-import=PIL._tkinter_finder \
    --collect-all UnityPy \
    --collect-all cairosvg \
    --collect-all svg.path \
    --additional-hooks-dir=hooks \
    fm_skin_builder/__main__.py
```

## Troubleshooting

### "no library called cairo was found"

This error means Cairo is not installed or not found by Python. Solutions:

1. **Install Cairo** using the instructions above for your platform
2. **Check your PATH** - Make sure the Cairo library directory is in your system PATH
3. **Verify installation** using the verification command above

### Windows: "cannot load library 'libcairo-2.dll'"

The DLL needs to be in a location where Python can find it:
- Copy `cairo.dll` to your Python's `DLLs` folder and rename it to `libcairo-2.dll`
- Or add the Cairo directory to your PATH environment variable

### macOS: "cannot load library 'libcairo.2.dylib'"

If Homebrew is installed but Cairo is not found:
```bash
# For ARM Macs (M1/M2/M3)
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

# For Intel Macs
export DYLD_LIBRARY_PATH="/usr/local/lib:$DYLD_LIBRARY_PATH"
```

Add this to your `~/.zshrc` or `~/.bash_profile` to make it permanent.

## CI/CD Builds

The GitHub Actions workflow automatically installs Cairo on all platforms during the build process. No manual setup is needed for CI builds.

## Alternative: Skip Cairo Features

If you don't need the asset catalogue feature that uses SVG processing, you can modify the code to make Cairo optional. However, this is not recommended as it will limit functionality.

## More Information

- [Cairo Graphics](https://www.cairographics.org/)
- [CairoSVG Documentation](https://cairosvg.org/)
- [cairocffi Documentation](https://cairocffi.readthedocs.io/)
