# Kreo Swarm Keyboard Backlight Control (macOS / Linux)

This project provides a modern GUI and CLI to control the backlight of the **Kreo Swarm keyboard** on **macOS** and **Linux** by directly communicating with the device over USB HID.

---

## Features
- **Modern GUI:** Built with CustomTkinter for a native macOS/Windows 11 look.
- **Color Picker:** Choose any RGB color for your keyboard.
- **Mode Selection:** Support for Static, Breathing, Wave, and Reactive modes.
- **Lightweight:** Minimal dependencies and small installation size.

---

## Requirements

### Hardware
- Kreo Swarm keyboard (USB mode)

### Software
- Python 3.8+
- Dependencies: `hidapi`, `customtkinter`

```bash
pip install -r requirements.txt
```

> **Note for Linux:** You may need udev rules or root permissions to access HID devices.

---

## Usage

### GUI (Recommended)
Launch the graphical interface:
```bash
python3 gui.py
```

### CLI
Set a specific color and mode via command line:
```bash
python3 swarmkreo/kreo_light.py 255 0 0 1
```
*(Usage: `python3 kreo_light.py R G B MODE_HEX`)*

---

## Project Structure
- `gui.py`: The main graphical application.
- `swarmkreo/controller.py`: Core HID communication logic.
- `swarmkreo/kreo_light.py`: Original CLI implementation.
- `requirements.txt`: Python dependencies.

---

## Technical Overview
- Vendor ID (VID): `0x258A`
- Product ID (PID): `0x010C`
- HID usage page: `0xFF00`
- HID interface number: `1`

---
