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
    'argv_emulation': True,
    'packages': ['customtkinter', 'swarmkreo', 'darkdetect'],
    'includes': ['tkinter', 'hid'], # Moved hid to includes
    'plist': {
        'CFBundleName': "Kreo Swarm RGB",
        'CFBundleDisplayName': "Kreo Swarm RGB",
        'CFBundleIdentifier': "com.pratyush.kreo-backlight",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHighResolutionCapable': True,
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
