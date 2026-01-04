"""
Witti Dotti - Cross-Platform Python Library (macOS/Windows/Linux)
==================================================================

A Python library to control the Witti Dotti 8x8 RGB LED pixel display
via Bluetooth Low Energy (BLE).

Based on reverse-engineering work from:
- https://github.com/MartyMacGyver/dotti-interfacing
- https://github.com/bertrandmartel/dotti-bluetooth-android

Requirements:
    pip install bleak

Usage:
    from dotti import Dotti
    
    async def main():
        dotti = Dotti()
        await dotti.connect()
        await dotti.set_all_pixels(255, 0, 0)  # All red
        await dotti.disconnect()
    
    asyncio.run(main())

Author: Claude (for Olivier Dobberkau / dkd Internet Service GmbH)
License: MIT
"""

import asyncio
from typing import Optional, Tuple, List
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice


# Dotti BLE UUIDs (from reverse engineering)
DOTTI_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
DOTTI_WRITE_CHAR_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"

# Dotti device name prefix
DOTTI_DEVICE_NAME = "Dotti"


class DottiColor:
    """Predefined colors for convenience."""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)


class Dotti:
    """
    Controller class for the Witti Dotti 8x8 RGB LED display.
    
    The Dotti is an 8x8 pixel LED matrix (64 pixels total) that can be
    controlled via Bluetooth Low Energy.
    
    Pixel layout (0-63):
        0  1  2  3  4  5  6  7
        8  9  10 11 12 13 14 15
        16 17 18 19 20 21 22 23
        24 25 26 27 28 29 30 31
        32 33 34 35 36 37 38 39
        40 41 42 43 44 45 46 47
        48 49 50 51 52 53 54 55
        56 57 58 59 60 61 62 63
    """
    
    GRID_SIZE = 8
    TOTAL_PIXELS = 64
    
    def __init__(self, address: Optional[str] = None):
        """
        Initialize the Dotti controller.
        
        Args:
            address: Optional MAC/UUID address of the Dotti device.
                    If not provided, will scan for nearby devices.
        """
        self.address = address
        self.client: Optional[BleakClient] = None
        self.device: Optional[BLEDevice] = None
        self._connected = False
        
        # Internal pixel buffer (8x8 RGB)
        self._pixel_buffer: List[List[Tuple[int, int, int]]] = [
            [(0, 0, 0) for _ in range(self.GRID_SIZE)]
            for _ in range(self.GRID_SIZE)
        ]
    
    @staticmethod
    async def scan(timeout: float = 10.0) -> List[BLEDevice]:
        """
        Scan for nearby Dotti devices.
        
        Args:
            timeout: Scan timeout in seconds.
            
        Returns:
            List of discovered Dotti devices.
        """
        print(f"Scanning for Dotti devices ({timeout}s)...")
        devices = await BleakScanner.discover(timeout=timeout)
        
        dotti_devices = []
        for device in devices:
            if device.name and DOTTI_DEVICE_NAME in device.name:
                dotti_devices.append(device)
                print(f"  Found: {device.name} [{device.address}]")
        
        if not dotti_devices:
            print("  No Dotti devices found.")
        
        return dotti_devices
    
    async def connect(self, timeout: float = 10.0) -> bool:
        """
        Connect to the Dotti device.
        
        If no address was provided during initialization, will scan
        and connect to the first Dotti device found.
        
        Args:
            timeout: Connection timeout in seconds.
            
        Returns:
            True if connection successful, False otherwise.
        """
        if self._connected:
            print("Already connected.")
            return True
        
        # If no address provided, scan for devices
        if not self.address:
            devices = await self.scan(timeout)
            if not devices:
                print("No Dotti device found to connect to.")
                return False
            self.device = devices[0]
            self.address = self.device.address
            print(f"Selected: {self.device.name} [{self.address}]")
        
        try:
            print(f"Connecting to {self.address}...")
            self.client = BleakClient(self.address)
            await self.client.connect(timeout=timeout)
            self._connected = True
            print("Connected successfully!")
            
            # Discover services (for debugging)
            services = self.client.services
            for service in services:
                print(f"  Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"    Characteristic: {char.uuid} - Properties: {char.properties}")
            
            return True
            
        except Exception as e:
            print(f"Connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from the Dotti device."""
        if self.client and self._connected:
            await self.client.disconnect()
            self._connected = False
            print("Disconnected.")
    
    @property
    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._connected and self.client is not None and self.client.is_connected
    
    async def _write(self, data: bytes):
        """
        Write raw data to the Dotti.
        
        Args:
            data: Bytes to write to the device.
        """
        if not self.is_connected:
            raise RuntimeError("Not connected to Dotti device.")
        
        await self.client.write_gatt_char(
            DOTTI_WRITE_CHAR_UUID,
            data,
            response=True
        )
        # Small delay to prevent overwhelming the device
        await asyncio.sleep(0.01)
    
    async def set_pixel(self, x: int, y: int, r: int, g: int, b: int):
        """
        Set a single pixel color.
        
        Args:
            x: X coordinate (0-7, left to right)
            y: Y coordinate (0-7, top to bottom)
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        if not (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
            raise ValueError(f"Coordinates must be 0-7, got x={x}, y={y}")
        
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Pixel index calculation (1-based for Dotti protocol)
        pixel_index = y * self.GRID_SIZE + x + 1

        # Command format: 0x07 0x02 <pixel_index> <r> <g> <b>
        data = bytes([0x07, 0x02, pixel_index, r, g, b])
        await self._write(data)
        
        # Update internal buffer
        self._pixel_buffer[y][x] = (r, g, b)
    
    async def set_pixel_by_index(self, index: int, r: int, g: int, b: int):
        """
        Set a pixel by its linear index (0-63).
        
        Args:
            index: Pixel index (0-63)
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        if not (0 <= index < self.TOTAL_PIXELS):
            raise ValueError(f"Index must be 0-63, got {index}")
        
        x = index % self.GRID_SIZE
        y = index // self.GRID_SIZE
        await self.set_pixel(x, y, r, g, b)
    
    async def set_all_pixels(self, r: int, g: int, b: int):
        """
        Set all pixels to the same color.
        
        Args:
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        
        # Command format: 0x06 0x01 <r> <g> <b>
        data = bytes([0x06, 0x01, r, g, b])
        await self._write(data)
        
        # Update internal buffer
        for y in range(self.GRID_SIZE):
            for x in range(self.GRID_SIZE):
                self._pixel_buffer[y][x] = (r, g, b)
    
    async def turn_off(self):
        """Turn off all pixels (set to black)."""
        await self.set_all_pixels(0, 0, 0)
    
    async def turn_on(self):
        """Turn on all pixels (set to white)."""
        await self.set_all_pixels(255, 255, 255)
    
    async def set_brightness(self, brightness: int):
        """
        Set global brightness level.
        
        Args:
            brightness: Brightness level (0-100)
        """
        brightness = max(0, min(100, brightness))
        
        # Command format: 0x06 0x02 <brightness>
        data = bytes([0x06, 0x02, brightness])
        await self._write(data)
    
    async def set_row(self, row: int, colors: List[Tuple[int, int, int]]):
        """
        Set all pixels in a row.
        
        Args:
            row: Row index (0-7)
            colors: List of 8 RGB tuples
        """
        if not (0 <= row < self.GRID_SIZE):
            raise ValueError(f"Row must be 0-7, got {row}")
        if len(colors) != self.GRID_SIZE:
            raise ValueError(f"Expected 8 colors, got {len(colors)}")
        
        for x, (r, g, b) in enumerate(colors):
            await self.set_pixel(x, row, r, g, b)
    
    async def set_column(self, col: int, colors: List[Tuple[int, int, int]]):
        """
        Set all pixels in a column.
        
        Args:
            col: Column index (0-7)
            colors: List of 8 RGB tuples
        """
        if not (0 <= col < self.GRID_SIZE):
            raise ValueError(f"Column must be 0-7, got {col}")
        if len(colors) != self.GRID_SIZE:
            raise ValueError(f"Expected 8 colors, got {len(colors)}")
        
        for y, (r, g, b) in enumerate(colors):
            await self.set_pixel(col, y, r, g, b)
    
    async def set_matrix(self, matrix: List[List[Tuple[int, int, int]]]):
        """
        Set the entire pixel matrix.
        
        Args:
            matrix: 8x8 list of RGB tuples
        """
        if len(matrix) != self.GRID_SIZE:
            raise ValueError(f"Expected 8 rows, got {len(matrix)}")
        
        for y, row in enumerate(matrix):
            if len(row) != self.GRID_SIZE:
                raise ValueError(f"Expected 8 columns in row {y}, got {len(row)}")
            for x, (r, g, b) in enumerate(row):
                await self.set_pixel(x, y, r, g, b)
    
    async def save_to_slot(self, slot: int):
        """
        Save current pixel configuration to a device slot.
        
        The Dotti has 8 internal slots (0-7) that can store
        pixel configurations for quick recall.
        
        Args:
            slot: Slot number (0-7)
        """
        if not (0 <= slot < 8):
            raise ValueError(f"Slot must be 0-7, got {slot}")
        
        # Command format: 0x06 0x06 <slot>
        data = bytes([0x06, 0x06, slot])
        await self._write(data)
    
    async def load_from_slot(self, slot: int):
        """
        Load and display a saved pixel configuration from a slot.
        
        Args:
            slot: Slot number (0-7)
        """
        if not (0 <= slot < 8):
            raise ValueError(f"Slot must be 0-7, got {slot}")
        
        # Command format: 0x06 0x05 <slot>
        data = bytes([0x06, 0x05, slot])
        await self._write(data)
    
    async def draw_character(self, char: str, color: Tuple[int, int, int], 
                            bg_color: Tuple[int, int, int] = (0, 0, 0)):
        """
        Draw a simple character on the display.
        
        Supports: 0-9, A-Z (uppercase)
        
        Args:
            char: Single character to display
            color: RGB color for the character
            bg_color: RGB background color
        """
        from .fonts import FONT_5X7
        
        char = char.upper()
        if char not in FONT_5X7:
            raise ValueError(f"Unsupported character: {char}")
        
        bitmap = FONT_5X7[char]
        
        # Clear display first
        await self.set_all_pixels(*bg_color)
        
        # Draw character (centered)
        offset_x = 1
        offset_y = 0
        
        for y, row in enumerate(bitmap):
            for x, pixel in enumerate(row):
                if pixel:
                    await self.set_pixel(x + offset_x, y + offset_y, *color)


class DottiAnimation:
    """Helper class for creating animations on the Dotti display."""
    
    def __init__(self, dotti: Dotti):
        self.dotti = dotti
    
    async def rainbow_cycle(self, cycles: int = 3, delay: float = 0.1):
        """
        Display a rainbow color cycle across all pixels.
        
        Args:
            cycles: Number of complete cycles
            delay: Delay between color changes in seconds
        """
        colors = [
            DottiColor.RED,
            DottiColor.ORANGE,
            DottiColor.YELLOW,
            DottiColor.GREEN,
            DottiColor.CYAN,
            DottiColor.BLUE,
            DottiColor.PURPLE,
            DottiColor.MAGENTA,
        ]
        
        for _ in range(cycles):
            for color in colors:
                await self.dotti.set_all_pixels(*color)
                await asyncio.sleep(delay)
    
    async def blink(self, color: Tuple[int, int, int], times: int = 3, 
                    on_time: float = 0.5, off_time: float = 0.5):
        """
        Blink all pixels.
        
        Args:
            color: RGB color to blink
            times: Number of blinks
            on_time: Duration of on state in seconds
            off_time: Duration of off state in seconds
        """
        for _ in range(times):
            await self.dotti.set_all_pixels(*color)
            await asyncio.sleep(on_time)
            await self.dotti.turn_off()
            await asyncio.sleep(off_time)
    
    async def scroll_text(self, text: str, color: Tuple[int, int, int],
                         delay: float = 0.3):
        """
        Scroll text across the display.
        
        Args:
            text: Text to scroll
            color: RGB color for text
            delay: Delay between frames in seconds
        """
        # Simplified scrolling - just display each character
        for char in text:
            try:
                await self.dotti.draw_character(char, color)
                await asyncio.sleep(delay)
            except ValueError:
                # Skip unsupported characters
                await self.dotti.turn_off()
                await asyncio.sleep(delay / 2)
    
    async def random_sparkle(self, duration: float = 5.0, delay: float = 0.1):
        """
        Create a random sparkle effect.
        
        Args:
            duration: Total duration in seconds
            delay: Delay between sparkles in seconds
        """
        import random
        
        start_time = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start_time < duration:
            x = random.randint(0, 7)
            y = random.randint(0, 7)
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            
            await self.dotti.set_pixel(x, y, r, g, b)
            await asyncio.sleep(delay)


# Simple 5x7 font for basic characters
FONT_5X7 = {
    '0': [
        [0, 1, 1, 1, 0, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 0, 0, 1, 1, 0],
        [1, 0, 1, 0, 1, 0],
        [1, 1, 0, 0, 1, 0],
        [1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
    '1': [
        [0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
    'A': [
        [0, 0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
    ],
    ' ': [
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
    ],
}


async def main():
    """Example usage of the Dotti library."""
    dotti = Dotti()
    
    try:
        # Connect to Dotti
        connected = await dotti.connect()
        if not connected:
            print("Could not connect to Dotti.")
            return
        
        # Demo animations
        animation = DottiAnimation(dotti)
        
        print("\n--- Rainbow Cycle ---")
        await animation.rainbow_cycle(cycles=2, delay=0.2)
        
        print("\n--- Blink Red ---")
        await animation.blink(DottiColor.RED, times=3)
        
        print("\n--- Random Sparkle ---")
        await animation.random_sparkle(duration=3.0)
        
        print("\n--- Turn Off ---")
        await dotti.turn_off()
        
    finally:
        await dotti.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
