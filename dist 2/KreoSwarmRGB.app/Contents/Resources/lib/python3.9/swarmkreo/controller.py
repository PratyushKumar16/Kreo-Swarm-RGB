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
            path = str(d.get("path", ""))
            
            # Check for matches with your specific hardware or strings
            is_kreo_vid = (v == self.VID_1 or v == self.VID_2)
            is_kreo_str = "Kreo" in product or "Kreo" in manufacturer or "Swarm" in product
            is_bt = "BT_" in path or "bluetooth" in path.lower()
            
            if is_kreo_vid or is_kreo_str:
                # Rank matches: Vendor page is best, then interface 1, then anything else for BT
                if up >= 0xFF00:
                    print(f"Found exact vendor interface: {product} at {path}")
                    return d
                if d.get("interface_number") == 1:
                    potential_matches.insert(0, d)
                elif is_bt:
                    potential_matches.append(d)
                else:
                    potential_matches.append(d)
        
        if potential_matches:
            match = potential_matches[0]
            print(f"Using best potential match: {match.get('product_string')} at {match.get('path')}")
            return match
        
        print("No Kreo hardware match found. Listing detected devices for debugging:")
        for d in devices[:15]:
             print(f" - {d.get('product_string')} (VID:{hex(d.get('vendor_id'))}, PID:{hex(d.get('product_id'))}, UP:{hex(d.get('usage_page',0))})")
        
        return None

    def connect(self):
        dev_info = self.find_device()
        if not dev_info:
            print("Kreo hardware not detected. Check USB connection.")
            return False
        
        try:
            self.device = hid.device()
            self.device.open_path(dev_info["path"])
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        if self.device:
            self.device.close()
            self.device = None

    def _from_hex(self, s):
        return bytes.fromhex("".join(s.split()))

    def _find_seed_offset(self, buf):
        hdr = b"\x06\x0a\x00\x00\x01\x00\x00\x02"
        p = buf.find(hdr)
        if p < 0: return -1
        start = p + len(hdr)
        for pat in (b"\xfe\xf7\xf5\x00", b"\x00\x00\x00\x00"):
            q = buf.find(pat, start, start+128)
            if q >= 0: return q
        return -1

    def apply_settings(self, r, g, b, mode_hex_str="01"):
        if not self.device and not self.connect():
            raise RuntimeError("Device not found or could not be opened")

        # Patch Palette
        palette_buf = bytearray(self._from_hex(self.PALETTE_HEX_TEMPLATE))
        off = self._find_seed_offset(palette_buf)
        if off != -1:
            palette_buf[off:off+3] = bytes([r & 0xff, g & 0xff, b & 0xff])
        
        # Patch Mode
        mode_hex = self.MODE_HEX_TEMPLATE
        mode_hex = mode_hex[:37] + mode_hex_str + mode_hex[38:]
        
        try:
            self.device.send_feature_report(bytes(palette_buf))
            time.sleep(0.05)
            self.device.send_feature_report(self._from_hex(mode_hex))
            return True
        except Exception as e:
            print(f"Error sending report: {e}")
            return False
        finally:
            self.disconnect()
