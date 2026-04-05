from setuptools import setup
import os
import sys
import customtkinter

# Find paths
ctk_path = os.path.dirname(customtkinter.__file__)

# Add current directory to path
sys.path.append(os.getcwd())

APP = ['gui.py']

# DATA_FILES handles resources
DATA_FILES = [
    ('customtkinter', [os.path.join(ctk_path, f) for f in os.listdir(ctk_path) if f.endswith(('.json', '.otf'))]),
]

# Walk through customtkinter for themes and assets
for root, dirs, files in os.walk(ctk_path):
    for d in dirs:
        dest_dir = os.path.join('customtkinter', os.path.relpath(os.path.join(root, d), ctk_path))
        src_dir = os.path.join(root, d)
        DATA_FILES.append((dest_dir, [os.path.join(src_dir, f) for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]))

OPTIONS = {
    'argv_emulation': False, # Disabled: known to cause crashes on newer macOS versions
    'packages': ['customtkinter', 'swarmkreo', 'darkdetect', 'hid'],
    'includes': ['tkinter'],
    'plist': {
        'CFBundleName': "KreoSwarmRGB",
        'CFBundleDisplayName': "Kreo Swarm RGB",
        'CFBundleIdentifier': "com.pratyush.kreoswarmrgb",
        'CFBundleVersion': "0.1.2",
        'CFBundleShortVersionString': "0.1.2",
        'NSHighResolutionCapable': True,
        'LSBackgroundOnly': False,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
