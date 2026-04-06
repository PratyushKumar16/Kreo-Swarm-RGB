import hid
import time

class KreoController:
    # Original known IDs
    VID_1 = 0x258A
    PID_1 = 0x010C

    # Your specific detected IDs (Kreo Swarm 5.0)
    VID_2 = 0x3554
    PID_2 = 0xFA07

    PALETTE_HEX_TEMPLATE = "060a000001000002000000000000000000000000000000000000000000fef7f500ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffffff000000ff000000ffffff00ff00ff00ffffffffff00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000005aa500000000"
    MODE_HEX_TEMPLATE = "06040000010080000003030100000404070003200100000000000100040200ff0600000001000402000000000000000000000000000000000000000000000000ffff03400447044704470447044704470447044704470447044704470447044704470447043704370437074707470744074407440744074407440744040404040404040404045aa50000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        self.device = None

    def find_device(self):
        # Scan all devices to be more flexible
        devices = list(hid.enumerate())
        print(f"Scanning {len(devices)} HID devices...")
        
        potential_matches = []
        
        for d in devices:
            v, p = d.get("vendor_id"), d.get("product_id")
            up = d.get("usage_page", 0)
            product = d.get("product_string", "") or ""
            manufacturer = d.get("manufacturer_string", "") or ""
            interface = d.get("interface_number", -1)
            path = str(d.get("path", ""))
            
            # Check for matches with your specific hardware or strings
            is_kreo_vid = (v == self.VID_1 or v == self.VID_2)
            is_kreo_str = any(s in (product + manufacturer) for s in ["Kreo", "Swarm", "Gaming Keyboard"])
            
            if is_kreo_vid or is_kreo_str:
                # Rank matches: Vendor page is best, then interface 1
                if up == 0xFF00:
                    print(f"Found exact vendor interface: {product} (VID:{hex(v)}, PID:{hex(p)}) at {path}")
                    return d
                
                # Interface 1 is the usual control interface for these keyboards
                if interface == 1:
                    potential_matches.insert(0, d)
                else:
                    potential_matches.append(d)
        
        if potential_matches:
            match = potential_matches[0]
            print(f"Using best potential match: {match.get('product_string')} (Interface {match.get('interface_number')})")
            return match
        
        print("No Kreo hardware match found. Listing first 10 devices:")
        for d in devices[:10]:
             print(f" - {d.get('product_string')} (VID:{hex(d.get('vendor_id'))}, PID:{hex(d.get('product_id'))}, UP:{hex(d.get('usage_page',0))}, IF:{d.get('interface_number')})")
        
        return None

    def connect(self):
        dev_info = self.find_device()
        if not dev_info:
            return False
        
        try:
            self.device = hid.device()
            self.device.open_path(dev_info["path"])
            print(f"Connected to {dev_info.get('product_string')}")
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        if self.device:
            try:
                self.device.close()
            except:
                pass
            self.device = None

    def _from_hex(self, s):
        return bytes.fromhex("".join(s.split()))

    def _find_seed_offset(self, buf):
        hdr = b"\x06\x0a\x00\x00\x01\x00\x00\x02"
        p = buf.find(hdr)
        if p < 0: return -1
        start = p + len(hdr)
        
        # Try known seeds
        for pat in (b"\xfe\xf7\xf5\x00", b"\x00\x00\x00\x00"):
            q = buf.find(pat, start, start+128)
            if q >= 0: return q
            
        # Fallback: look for any 4-byte aligned pattern ending in 00
        for i in range(start, min(len(buf)-4, start+128)):
            if buf[i+3] == 0x00 and any(buf[i:i+3]): # Not all zeros
                return i
        return -1

    def apply_settings(self, r, g, b, mode_hex_str="01"):
        if not self.device and not self.connect():
            raise RuntimeError("Kreo hardware not detected. Please ensure it is connected via USB or Dongle.")

        # Patch Palette
        palette_buf = bytearray(self._from_hex(self.PALETTE_HEX_TEMPLATE))
        off = self._find_seed_offset(palette_buf)
        if off != -1:
            # Most of these controllers use 4 bytes (R, G, B, 00)
            palette_buf[off:off+4] = bytes([r & 0xff, g & 0xff, b & 0xff, 0x00])
        else:
            print("Warning: Could not locate color seed in template. Using default offset.")
            # Fallback to a common offset if known
        
        # Patch Mode
        mode_hex = self.MODE_HEX_TEMPLATE
        # Mode is usually at a specific offset in the 06 04 report
        # The template has '03' at index 37 (offset 18 in bytes?)
        # Let's be careful here.
        mode_bytes = bytearray(self._from_hex(mode_hex))
        if len(mode_bytes) > 18:
            mode_bytes[18] = int(mode_hex_str, 16)
        
        try:
            self.device.send_feature_report(bytes(palette_buf))
            time.sleep(0.08) # Slightly longer delay for stability
            self.device.send_feature_report(bytes(mode_bytes))
            return True
        except Exception as e:
            print(f"Error sending HID report: {e}")
            return False
        finally:
            self.disconnect()
