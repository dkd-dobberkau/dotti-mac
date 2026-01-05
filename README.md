# Dotti-Mac

Python library and web editor for the Witti Dotti 8x8 RGB LED display on macOS.

## Features

- **Python Library** (`dotti.py`) - Full BLE control of the Dotti display
- **Web Editor** - Browser-based pixel editor with HTMX and FastAPI
- **Hardware Slots** - Save/load images to Dotti's 8 internal slots for instant switching
- **Preset Patterns** - Built-in emojis: heart, smiley, star, sun, ghost, alien, fire, rainbow

## Requirements

- macOS (uses bleak for BLE)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/dotti-mac.git
cd dotti-mac

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Quick Start

### Python Library

```python
import asyncio
from dotti import Dotti

async def main():
    dotti = Dotti()
    await dotti.connect()

    # Set a single pixel (red at position 0,0)
    await dotti.set_pixel(0, 0, 255, 0, 0)

    # Fill entire display with blue
    await dotti.fill(0, 0, 255)

    # Save to hardware slot 0
    await dotti.save_to_slot(0)

    # Load from hardware slot 0 (instant!)
    await dotti.load_from_slot(0)

    await dotti.disconnect()

asyncio.run(main())
```

### Web Editor

```bash
# Start the web editor
uv run python -m uvicorn editor.app:app --reload

# Open in browser
open http://127.0.0.1:8000
```

## Web Editor Features

- **8x8 Pixel Grid** - Click to paint pixels
- **Color Palette** - Quick-select colors (red, green, blue, yellow, magenta, cyan, orange, white, black)
- **Preset Patterns** - Load built-in emojis with one click
- **Hardware Slots (0-7)** - Save/Load buttons for instant image switching (~0.3s)
- **Database Storage** - Save named images to SQLite database
- **Clear/Random** - Reset or fill with random colors

## BLE Protocol

The Dotti uses Bluetooth Low Energy with:
- Service UUID: `0000fff0-0000-1000-8000-00805f9b34fb`
- Write Characteristic: `0000fff3-0000-1000-8000-00805f9b34fb`

### Commands

| Command | Format | Description |
|---------|--------|-------------|
| Set Pixel | `07 02 [index] [r] [g] [b]` | Set single pixel (index 1-64) |
| Fill All | `06 01 [r] [g] [b]` | Fill all pixels with one color |
| Save Slot | `06 05 [slot]` | Save display to slot (0-7) |
| Load Slot | `06 06 [slot]` | Load display from slot (0-7) |

## BLE Scanner

A standalone Bluetooth Low Energy scanner with manufacturer identification and Apple device type detection.

### Usage

```bash
# Basic scan (10 seconds)
uv run python ble_scanner.py

# Quick scan (5 seconds)
uv run python ble_scanner.py --timeout 5

# Filter by device name
uv run python ble_scanner.py --filter Dotti

# Group by manufacturer
uv run python ble_scanner.py --group

# Sort by name or manufacturer
uv run python ble_scanner.py --sort name
uv run python ble_scanner.py --sort manufacturer

# Live mode (show devices as found)
uv run python ble_scanner.py --live

# Verbose mode (show raw data)
uv run python ble_scanner.py --verbose
```

### Features

- **Manufacturer Identification**: Recognizes 290+ Bluetooth SIG registered companies (Apple, Microsoft, Samsung, etc.)
- **Apple Device Detection**: Decodes Apple Continuity Protocol to identify:
  - FindMy devices (AirTags) with ownership status
  - AirPods, Beats, and other audio devices
  - Apple Watch activity state
  - AirPlay targets (Apple TV, HomePod)
  - Handoff, AirDrop, and other services
- **Sorting & Grouping**: Sort by signal strength (RSSI), name, or manufacturer; group by manufacturer
- **Signal Strength**: RSSI values in dBm (closer to 0 = stronger signal)

### Example Output

```
Device: Schlüssel von Olivier
  Address: 2AEB00BA-8AC1-72CD-E68A-01D2A646311F
  RSSI: -57 dBm
  Manufacturer: Apple, Inc. (0x004C)
  Apple Type: FindMy Device (Owned (maintained))

Device: Unknown
  Address: 246D70D7-DD70-B196-1180-9B610997FFFA
  RSSI: -64 dBm
  Manufacturer: Apple, Inc. (0x004C)
  Apple Type: Nearby Info - Activity: Watch On Wrist
```

## Project Structure

```
dotti-mac/
├── dotti.py              # Main BLE library
├── ble_scanner.py        # BLE device scanner
├── requirements.txt      # Python dependencies
├── editor/
│   ├── app.py            # FastAPI backend
│   ├── database.py       # SQLAlchemy models
│   ├── templates/
│   │   ├── editor.html   # Main editor page
│   │   └── partials/     # HTMX partials
│   └── static/
│       └── style.css     # Dark theme styling
└── dotti.db              # SQLite database (created on first run)
```

## Pixel Layout

The Dotti has an 8x8 LED grid. Pixels are addressed by x,y coordinates (0-7):

```
     x: 0  1  2  3  4  5  6  7
    ┌──────────────────────────┐
y:0 │  1  2  3  4  5  6  7  8 │
y:1 │  9 10 11 12 13 14 15 16 │
y:2 │ 17 18 19 20 21 22 23 24 │
y:3 │ 25 26 27 28 29 30 31 32 │
y:4 │ 33 34 35 36 37 38 39 40 │
y:5 │ 41 42 43 44 45 46 47 48 │
y:6 │ 49 50 51 52 53 54 55 56 │
y:7 │ 57 58 59 60 61 62 63 64 │
    └──────────────────────────┘
```

Note: Internal pixel indices are 1-based (1-64), not 0-based.

## Troubleshooting

### macOS: Bluetooth Permission

macOS requires Bluetooth access for Python. If connection fails:

1. Open **System Settings → Privacy & Security → Bluetooth**
2. Add your Terminal or Python executable

### Connection Issues

- Keep the Dotti close to your computer (< 5m)
- Make sure no other apps are connected to the Dotti
- Power-cycle the Dotti device

## Credits

Based on reverse-engineering work from:
- [MartyMacGyver/dotti-interfacing](https://github.com/MartyMacGyver/dotti-interfacing)
- [bertrandmartel/dotti-bluetooth-android](https://github.com/bertrandmartel/dotti-bluetooth-android)

## License

MIT License - see [LICENSE](LICENSE)
