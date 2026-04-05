
import os
import sys

# Get the path to the Frameworks folder inside the .app bundle
executable_dir = os.path.dirname(sys.executable)
frameworks_dir = os.path.abspath(os.path.join(executable_dir, "..", "Frameworks"))

# Force the dynamic linker to look in the Frameworks folder
if os.path.exists(frameworks_dir):
    os.environ["DYLD_LIBRARY_PATH"] = frameworks_dir + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")
    # For newer hid libraries that might be looking for a specific name
    # we can also set the HIDAPI_LIB_PATH if the library supports it
    os.environ["HIDAPI_LIB_PATH"] = os.path.join(frameworks_dir, "libhidapi.dylib")
