import os
import sys
import customtkinter
import subprocess

# Find customtkinter path
ctk_path = os.path.dirname(customtkinter.__file__)

# Find libhidapi.dylib
libhidapi_path = None
try:
    # Try brew first
    brew_prefix = subprocess.check_output(['brew', '--prefix', 'hidapi'], text=True, stderr=subprocess.DEVNULL).strip()
    p = os.path.join(brew_prefix, 'lib', 'libhidapi.dylib')
    if os.path.exists(p):
        libhidapi_path = p
except:
    pass

if not libhidapi_path:
    # Common locations
    for p in ['/opt/homebrew/lib/libhidapi.dylib', '/usr/local/lib/libhidapi.dylib']:
        if os.path.exists(p):
            libhidapi_path = p
            break

APP = ['gui.py']

# DATA_FILES handles resources
DATA_FILES = []

# Include libhidapi.dylib in Frameworks if found
if libhidapi_path:
    print(f"Including libhidapi.dylib from {libhidapi_path}")
    DATA_FILES.append(('Frameworks', [libhidapi_path]))

# Walk through customtkinter for themes and assets
for root, dirs, files in os.walk(ctk_path):
    for d in dirs:
        if d in ['assets', 'themes']:
            dest_dir = os.path.join('customtkinter', os.path.relpath(os.path.join(root, d), ctk_path))
            src_dir = os.path.join(root, d)
            file_list = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
            if file_list:
                DATA_FILES.append((dest_dir, file_list))

# Also include top-level json/otf files
DATA_FILES.append(('customtkinter', [os.path.join(ctk_path, f) for f in os.listdir(ctk_path) if f.endswith(('.json', '.otf'))]))

OPTIONS = {
    'argv_emulation': False,
    'packages': ['customtkinter', 'swarmkreo', 'darkdetect', 'Cocoa'],
    'includes': ['tkinter', 'hid'],
    'plist': {
        'CFBundleName': "KreoSwarmRGB",
        'CFBundleDisplayName': "Kreo Swarm RGB",
        'CFBundleIdentifier': "com.pratyush.kreoswarmrgb",
        'CFBundleVersion': "1.0.3",
        'CFBundleShortVersionString': "1.0.3",
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
        'NSRequiresAquaSystemAppearance': False,
    }
}

from setuptools import setup

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
