"""
PyInstaller runtime hook for cairocffi.
This hook helps cairocffi find the Cairo DLL when running from a PyInstaller bundle.
"""
import os
import sys

# When running from PyInstaller, sys._MEIPASS contains the path to the extracted files
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Add the PyInstaller extraction directory to the DLL search path
    dll_directory = sys._MEIPASS

    # On Windows, add to PATH and DLL search directories
    if sys.platform == 'win32':
        # Add to PATH so Windows can find DLLs
        os.environ['PATH'] = dll_directory + os.pathsep + os.environ.get('PATH', '')

        # On Python 3.8+, also add to DLL directory (more secure)
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(dll_directory)

    # On Unix-like systems, add to library path
    elif sys.platform == 'darwin':
        os.environ['DYLD_LIBRARY_PATH'] = dll_directory + os.pathsep + os.environ.get('DYLD_LIBRARY_PATH', '')
    else:  # Linux
        os.environ['LD_LIBRARY_PATH'] = dll_directory + os.pathsep + os.environ.get('LD_LIBRARY_PATH', '')
