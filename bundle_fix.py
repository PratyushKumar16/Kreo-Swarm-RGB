
import os
import sys

def apply_bundle_fixes():
    # Only apply if we are running in a bundled .app
    if ".app/Contents/Resources" in os.path.abspath(sys.executable) or getattr(sys, 'frozen', False):
        executable_dir = os.path.dirname(sys.executable)
        contents_dir = os.path.abspath(os.path.join(executable_dir, ".."))
        
        # Check both possible locations for Frameworks
        frameworks_dir = os.path.join(contents_dir, "Frameworks")
        res_frameworks_dir = os.path.join(contents_dir, "Resources", "Frameworks")
        
        chosen_fw = None
        if os.path.exists(frameworks_dir):
            chosen_fw = frameworks_dir
        elif os.path.exists(res_frameworks_dir):
            chosen_fw = res_frameworks_dir
            
        if chosen_fw:
            # Help hidapi find the library
            os.environ["DYLD_LIBRARY_PATH"] = chosen_fw + ":" + os.environ.get("DYLD_LIBRARY_PATH", "")
            os.environ["HIDAPI_LIB_PATH"] = os.path.join(chosen_fw, "libhidapi.dylib")
            print(f"Bundle fix: Set HIDAPI_LIB_PATH to {os.environ['HIDAPI_LIB_PATH']}")
        
        # Help customtkinter find its assets in Resources
        resources_dir = os.path.join(contents_dir, "Resources")
        if os.path.exists(resources_dir):
            if resources_dir not in sys.path:
                sys.path.insert(0, resources_dir)
    
apply_bundle_fixes()
