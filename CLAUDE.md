# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Dotti-macOS is a cross-platform Python library for controlling the Witti Dotti 8x8 RGB LED pixel display via Bluetooth Low Energy (BLE). It uses the `bleak` library for BLE communication and provides an async/await API.

## Commands

```bash
# Create virtual environment (einmalig)
uv venv

# Install dependencies
uv pip install -e .

# Install with development dependencies
uv pip install -e ".[dev]"

# Run the main library (scans and demos)
uv run python dotti.py

# Run the Solr monitor
uv run python solr_monitor.py --url http://localhost:8983/solr/core_de

# Run the CI/CD status indicator
uv run python ci_status.py --status success
uv run python ci_status.py --webhook --port 8080

# Run tests
uv run pytest
uv run pytest -v tests/test_specific.py::test_function

# Format code
uv run black .

# Type checking
uv run mypy .
```

## Architecture

### Core Library (`dotti.py`)
- `Dotti` class: Main controller for the LED display via BLE
  - Manages BLE connection using `BleakClient`
  - Maintains internal 8x8 pixel buffer
  - Sends commands via GATT characteristic `0xfff3`
- `DottiColor`: Predefined RGB color constants
- `DottiAnimation`: Helper for rainbow cycles, blink, sparkle, text scroll
- `FONT_5X7`: Built-in bitmap font for character display

### BLE Protocol
- Service UUID: `0000fff0-0000-1000-8000-00805f9b34fb`
- Write characteristic: `0000fff3-0000-1000-8000-00805f9b34fb`
- **Important**: Pixel index is 1-based (1-64), not 0-based
- **Important**: Use `response=True` when writing GATT characteristics
- Command formats:
  - Single pixel: `0x07 0x02 <index 1-64> <r> <g> <b>`
  - All pixels: `0x06 0x01 <r> <g> <b>`
  - Brightness: `0x06 0x02 <level>`
  - Save slot: `0x06 0x06 <slot>`
  - Load slot: `0x06 0x05 <slot>`

### Application Scripts
- `solr_monitor.py`: Monitors Apache Solr index status, displays on Dotti
- `ci_status.py`: Shows CI/CD pipeline status (success/failure/building icons), includes webhook server for GitLab/GitHub integration

### Pixel Layout
8x8 grid, indices 0-63 from top-left to bottom-right, row by row. Coordinates: x (0-7 left-to-right), y (0-7 top-to-bottom).

## Key Patterns

- All Dotti operations are async (`async def`, `await`)
- Small delay (50ms) after each write to prevent overwhelming the device
- RGB values clamped to 0-255
- Device slots 0-7 for storing/loading configurations
