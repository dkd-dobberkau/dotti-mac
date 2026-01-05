"""
BLE Scanner - Scan for nearby Bluetooth Low Energy devices
===========================================================

Usage:
    uv run python ble_scanner.py
    uv run python ble_scanner.py --timeout 20
    uv run python ble_scanner.py --filter Dotti
"""

import asyncio
import argparse
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData


# Bluetooth SIG Company Identifiers
# Source: https://www.bluetooth.com/specifications/assigned-numbers/
COMPANY_IDENTIFIERS = {
    0x0000: "Ericsson Technology Licensing",
    0x0001: "Nokia Mobile Phones",
    0x0002: "Intel Corp.",
    0x0003: "IBM Corp.",
    0x0004: "Toshiba Corp.",
    0x0005: "3Com",
    0x0006: "Microsoft",
    0x0007: "Lucent",
    0x0008: "Motorola",
    0x0009: "Infineon Technologies AG",
    0x000A: "Qualcomm Technologies International (QTIL)",
    0x000B: "Silicon Wave",
    0x000C: "Digianswer A/S",
    0x000D: "Texas Instruments Inc.",
    0x000E: "Parthus Technologies Inc.",
    0x000F: "Broadcom Corporation",
    0x0010: "Mitel Semiconductor",
    0x0011: "Widcomm, Inc.",
    0x0012: "Zeevo, Inc.",
    0x0013: "Atmel Corporation",
    0x0014: "Mitsubishi Electric Corporation",
    0x0015: "RTX Telecom A/S",
    0x0016: "KC Technology Inc.",
    0x0017: "Newlogic",
    0x0018: "Transilica, Inc.",
    0x0019: "Rohde & Schwarz GmbH & Co. KG",
    0x001A: "TTPCom Limited",
    0x001B: "Signia Technologies, Inc.",
    0x001C: "Conexant Systems Inc.",
    0x001D: "Qualcomm",
    0x001E: "Inventel",
    0x001F: "AVM Berlin",
    0x0020: "BandSpeed, Inc.",
    0x0021: "Mansella Ltd",
    0x0022: "NEC Corporation",
    0x0023: "WavePlus Technology Co., Ltd.",
    0x0024: "Alcatel",
    0x0025: "NXP Semiconductors",
    0x0026: "C Technologies",
    0x0027: "Open Interface",
    0x0028: "R F Micro Devices",
    0x0029: "Hitachi Ltd",
    0x002A: "Symbol Technologies, Inc.",
    0x002B: "Tenovis",
    0x002C: "Macronix International Co. Ltd.",
    0x002D: "GCT Semiconductor",
    0x002E: "Norwood Systems",
    0x002F: "MewTel Technology Inc.",
    0x0030: "ST Microelectronics",
    0x0031: "Synopsys, Inc.",
    0x0032: "Red-M (Communications) Ltd",
    0x0033: "Commil Ltd",
    0x0034: "Computer Access Technology Corporation (CATC)",
    0x0035: "Eclipse (HQ Espana) S.L.",
    0x0036: "Renesas Electronics Corporation",
    0x0037: "Mobilian Corporation",
    0x0038: "Syntronix Corporation",
    0x0039: "Integrated System Solution Corp.",
    0x003A: "Panasonic Corporation",
    0x003B: "Gennum Corporation",
    0x003C: "Research In Motion",
    0x003D: "IPextreme, Inc.",
    0x003E: "Systems and Chips, Inc.",
    0x003F: "Bluetooth SIG, Inc.",
    0x0040: "Seiko Epson Corporation",
    0x0041: "Integrated Silicon Solution Taiwan, Inc.",
    0x0042: "CONWISE Technology Corporation Ltd",
    0x0043: "PARROT SA",
    0x0044: "Socket Mobile",
    0x0045: "Atheros Communications, Inc.",
    0x0046: "MediaTek, Inc.",
    0x0047: "Bluegiga",
    0x0048: "Marvell Technology Group Ltd.",
    0x0049: "3DSP Corporation",
    0x004A: "Accel Semiconductor Ltd.",
    0x004B: "Continental Automotive Systems",
    0x004C: "Apple, Inc.",
    0x004D: "Staccato Communications, Inc.",
    0x004E: "Avago Technologies",
    0x004F: "APT Licensing Ltd.",
    0x0050: "SiRF Technology, Inc.",
    0x0051: "Tzero Technologies, Inc.",
    0x0052: "J&M Corporation",
    0x0053: "Free2move AB",
    0x0054: "3DiJoy Corporation",
    0x0055: "Plantronics, Inc.",
    0x0056: "Sony Ericsson Mobile Communications",
    0x0057: "Harman International Industries, Inc.",
    0x0058: "Vizio, Inc.",
    0x0059: "Nordic Semiconductor ASA",
    0x005A: "EM Microelectronic-Marin SA",
    0x005B: "Ralink Technology Corporation",
    0x005C: "Belkin International, Inc.",
    0x005D: "Realtek Semiconductor Corporation",
    0x005E: "Stonestreet One, LLC",
    0x005F: "Wicentric, Inc.",
    0x0060: "RivieraWaves S.A.S",
    0x0061: "RDA Microelectronics",
    0x0062: "Gibson Guitars",
    0x0063: "MiCommand Inc.",
    0x0064: "Band XI International, LLC",
    0x0065: "Hewlett-Packard Company",
    0x0066: "9Solutions Oy",
    0x0067: "GN Netcom A/S",
    0x0068: "General Motors",
    0x0069: "A&D Engineering, Inc.",
    0x006A: "MindTree Ltd.",
    0x006B: "Polar Electro OY",
    0x006C: "Beautiful Enterprise Co., Ltd.",
    0x006D: "BriarTek, Inc.",
    0x006E: "Summit Data Communications, Inc.",
    0x006F: "Sound ID",
    0x0070: "Monster, LLC",
    0x0071: "connectBlue AB",
    0x0072: "ShangHai Super Smart Electronics Co. Ltd.",
    0x0073: "Group Sense Ltd.",
    0x0074: "Zomm, LLC",
    0x0075: "Samsung Electronics Co. Ltd.",
    0x0076: "Creative Technology Ltd.",
    0x0077: "Laird Technologies",
    0x0078: "Nike, Inc.",
    0x0079: "lesswire AG",
    0x007A: "MStar Semiconductor, Inc.",
    0x007B: "Hanlynn Technologies",
    0x007C: "A & R Cambridge",
    0x007D: "Seers Technology Co., Ltd.",
    0x007E: "Sports Tracking Technologies Ltd.",
    0x007F: "Autonet Mobile",
    0x0080: "DeLorme Publishing Company, Inc.",
    0x0081: "WuXi Vimicro",
    0x0082: "Sennheiser Communications A/S",
    0x0083: "TimeKeeping Systems, Inc.",
    0x0084: "Ludus Helsinki Ltd.",
    0x0085: "BlueRadios, Inc.",
    0x0086: "Equinux AG",
    0x0087: "Garmin International, Inc.",
    0x0088: "Ecotest",
    0x0089: "GN ReSound A/S",
    0x008A: "Jawbone",
    0x008B: "Topcon Positioning Systems, LLC",
    0x008C: "Gimbal Inc.",
    0x008D: "Zscan Software",
    0x008E: "Quintic Corp",
    0x008F: "Telit Wireless Solutions GmbH",
    0x0090: "Funai Electric Co., Ltd.",
    0x0091: "Advanced PANMOBIL systems GmbH & Co. KG",
    0x0092: "ThinkOptics, Inc.",
    0x0093: "Universal Electronics, Inc.",
    0x0094: "Airoha Technology Corp.",
    0x0095: "NEC Lighting, Ltd.",
    0x0096: "ODM Technology, Inc.",
    0x0097: "ConnecteDevice Ltd.",
    0x0098: "zero1.tv GmbH",
    0x0099: "i.Tech Dynamic Global Distribution Ltd.",
    0x009A: "Alpwise",
    0x009B: "Jiangsu Toppower Automotive Electronics Co., Ltd.",
    0x009C: "Colorfy, Inc.",
    0x009D: "Geoforce Inc.",
    0x009E: "Bose Corporation",
    0x009F: "Suunto Oy",
    0x00A0: "Kensington Computer Products Group",
    0x00A1: "SR-Medizinelektronik",
    0x00A2: "Vertu Corporation Limited",
    0x00A3: "Meta Watch Ltd.",
    0x00A4: "LINAK A/S",
    0x00A5: "OTL Dynamics LLC",
    0x00A6: "Panda Ocean Inc.",
    0x00A7: "Visteon Corporation",
    0x00A8: "ARP Devices Limited",
    0x00A9: "MARELLI EUROPE S.P.A.",
    0x00AA: "CAEN RFID srl",
    0x00AB: "Ingenieur-Systemgruppe Zahn GmbH",
    0x00AC: "Green Throttle Games",
    0x00AD: "Peter Systemtechnik GmbH",
    0x00AE: "Omegawave Oy",
    0x00AF: "Cinetix",
    0x00B0: "Passif Semiconductor Corp",
    0x00B1: "Saris Cycling Group, Inc",
    0x00B2: "Bekey A/S",
    0x00B3: "Clarinox Technologies Pty. Ltd.",
    0x00B4: "BDE Technology Co., Ltd.",
    0x00B5: "Swirl Networks",
    0x00B6: "Meso international",
    0x00B7: "TreLab Ltd",
    0x00B8: "Qualcomm Innovation Center, Inc. (QuIC)",
    0x00B9: "Johnson Controls, Inc.",
    0x00BA: "Starkey Hearing Technologies",
    0x00BB: "S-Power Electronics Limited",
    0x00BC: "Ace Sensor Inc",
    0x00BD: "Aplix Corporation",
    0x00BE: "AAMP of America",
    0x00BF: "Stalmart Technology Limited",
    0x00C0: "AMICCOM Electronics Corporation",
    0x00C1: "Shenzhen Excelsecu Data Technology Co.,Ltd",
    0x00C2: "Geneq Inc.",
    0x00C3: "adidas AG",
    0x00C4: "LG Electronics",
    0x00C5: "Onset Computer Corporation",
    0x00C6: "Selfly BV",
    0x00C7: "Quuppa Oy.",
    0x00C8: "GeLo Inc",
    0x00C9: "Evluma",
    0x00CA: "MC10",
    0x00CB: "Binauric SE",
    0x00CC: "Beats Electronics",
    0x00CD: "Microchip Technology Inc.",
    0x00CE: "Elgato Systems GmbH",
    0x00CF: "ARCHOS SA",
    0x00D0: "Dexcom, Inc.",
    0x00D1: "Polar Electro Europe B.V.",
    0x00D2: "Dialog Semiconductor B.V.",
    0x00D3: "Taixingbang Technology (HK) Co,. LTD.",
    0x00D4: "Kawantech",
    0x00D5: "Austco Communication Systems",
    0x00D6: "Timex Group USA, Inc.",
    0x00D7: "Qualcomm Technologies, Inc.",
    0x00D8: "Qualcomm Connected Experiences, Inc.",
    0x00D9: "Voyetra Turtle Beach",
    0x00DA: "txtr GmbH",
    0x00DB: "Biosentronics",
    0x00DC: "Procter & Gamble",
    0x00DD: "Hosiden Corporation",
    0x00DE: "Consumers Union",
    0x00DF: "Swingback Technologies Corp.",
    0x00E0: "Google",
    0x00E1: "Espressif Incorporated",
    0x00E2: "Aruba Networks",
    0x00E3: "Skydrop",
    0x00E4: "Edyn",
    0x00E5: "Shenzhen Huiding Technology Co.,Ltd.",
    0x00E6: "Wirepaths",
    0x00E7: "RadioPulse Inc",
    0x00E8: "Sensirion AG",
    0x00E9: "Versa",
    0x00EA: "MikroElektronika",
    0x00EB: "ETA SA",
    0x00EC: "Maxell, Ltd.",
    0x00ED: "Interaxon Inc.",
    0x00EE: "Elbit Systems Ltd",
    0x00EF: "Nod, Inc.",
    0x00F0: "B-B-Smartworx Inc.",
    0x00F1: "Acer, Inc.",
    0x00F2: "Laird Connectivity",
    0x00F3: "JIN CO, Ltd",
    0x00F4: "SZ DJI Technology Co.,Ltd",
    0x00F5: "Guillemot Corporation",
    0x00F6: "GIANT MANUFACTURING CO. LTD",
    0x00F7: "Tacx b.v.",
    0x00F8: "Apollo Neuroscience, Inc.",
    0x00F9: "Xiaomi Inc.",
    0x00FA: "Thinkware",
    0x00FB: "Swiftronics AB",
    0x00FC: "Uwatec AG",
    0x00FD: "Biosentec",
    0x00FE: "ROLI Ltd",
    0x00FF: "Dell Computer Corporation",
    0x0100: "Logitech International SA",
    0x0101: "Comarch SA",
    0x0102: "JVC KENWOOD Corporation",
    0x0103: "Bang & Olufsen A/S",
    0x0104: "Fitbit LLC",
    0x0131: "Huawei Technologies Co., Ltd.",
    0x0157: "Tile, Inc.",
    0x015D: "Anker Innovations Limited",
    0x0171: "Amazon.com Services, Inc.",
    0x01A7: "Peloton Interactive Inc.",
    0x022B: "Oura Health Oy",
    0x02E5: "Sonos, Inc.",
    0x0499: "Ruuvi Innovations Ltd.",
    0x0822: "IKEA of Sweden",
    0x08A9: "Brava Home Inc.",
    0x0D8A: "Nothing Technology Limited",
    # Higher range IDs (newer registrations)
    0xAEF0: "Unknown (ID: 0xAEF0)",
}


# Apple Continuity Protocol Message Types
# Source: https://github.com/furiousMAC/continuity
APPLE_CONTINUITY_TYPES = {
    0x01: "AirPrint",
    0x02: "AirDrop",
    0x03: "HomeKit",
    0x05: "AirDrop",
    0x06: "HomeKit",
    0x07: "AirPods / Proximity Pairing",
    0x08: "Hey Siri",
    0x09: "AirPlay Target",
    0x0A: "AirPlay Source",
    0x0B: "MagicSwitch",
    0x0C: "Handoff",
    0x0D: "Tethering Target",
    0x0E: "Tethering Source",
    0x0F: "Nearby Action",
    0x10: "Nearby Info",
    0x12: "FindMy (AirTag/Device)",
    0x13: "FindMy Accessory",
    0x14: "FindMy Location",
    0x16: "AirPods Pairing",
}

# Apple Nearby Action subtypes (0x0F)
APPLE_NEARBY_ACTIONS = {
    0x01: "Apple TV Setup",
    0x04: "Mobile Backup",
    0x05: "Watch Setup",
    0x06: "Apple TV Pairing",
    0x07: "Internet Tethering",
    0x08: "Wi-Fi Password",
    0x09: "iOS Setup",
    0x0A: "Repair",
    0x0B: "Speaker Setup",
    0x0C: "Apple Pay",
    0x0D: "Whole Home Audio Setup",
    0x0E: "Developer Tools",
    0x0F: "Answered Call",
    0x10: "Ended Call",
    0x11: "DD Ping",
    0x12: "DD Pong",
    0x13: "Remote Auto Fill",
    0x14: "Companion Link",
    0x15: "Remote Management",
    0x16: "Remote Auto Fill Pong",
    0x17: "Remote Display",
}

# FindMy device status hints
FINDMY_STATUS = {
    0x00: "Owned",
    0x01: "Shared",
    0x02: "Owned (maintained)",
    0x03: "Separated",
    0x04: "Unknown",
}


def decode_apple_advertising(data: bytes) -> str:
    """Decode Apple Continuity Protocol advertising data."""
    if len(data) < 2:
        return None

    details = []
    offset = 0

    while offset < len(data):
        if offset + 2 > len(data):
            break

        msg_type = data[offset]
        msg_len = data[offset + 1]

        if offset + 2 + msg_len > len(data):
            break

        msg_data = data[offset + 2:offset + 2 + msg_len]

        type_name = APPLE_CONTINUITY_TYPES.get(msg_type, f"Unknown (0x{msg_type:02X})")

        # Special handling for specific types
        if msg_type == 0x12:  # FindMy
            if len(msg_data) >= 1:
                status = msg_data[0] >> 6
                status_name = FINDMY_STATUS.get(status, "Unknown")
                details.append(f"FindMy Device ({status_name})")
            else:
                details.append("FindMy Device")
        elif msg_type == 0x10:  # Nearby Info
            if len(msg_data) >= 1:
                action_code = msg_data[0]
                # Device activity states
                activities = {
                    0x01: "Activity: Off",
                    0x03: "Activity: Idle",
                    0x05: "Activity: Audio",
                    0x07: "Activity: Screen On",
                    0x09: "Activity: Screen On (video)",
                    0x0A: "Activity: Watch On Wrist",
                    0x0B: "Activity: Recent Call",
                    0x0D: "Activity: Active Call",
                    0x11: "Activity: Home Screen",
                    0x13: "Activity: Using Device",
                    0x17: "Activity: Driving",
                    0x18: "Activity: Transportation",
                    0x1A: "Activity: Navigation",
                    0x1B: "Activity: Workout",
                    0x1C: "Activity: Siri",
                }
                activity = activities.get(action_code, f"Activity: 0x{action_code:02X}")
                details.append(f"Nearby Info - {activity}")
            else:
                details.append("Nearby Info")
        elif msg_type == 0x07:  # Proximity Pairing (AirPods etc.)
            device_models = {
                0x0220: "AirPods",
                0x0320: "Powerbeats3",
                0x0520: "BeatsX",
                0x0620: "AirPods Pro",
                0x0A20: "AirPods Max",
                0x0E20: "AirPods Pro 2",
                0x1020: "Beats Fit Pro",
                0x1220: "AirPods 3",
                0x1420: "AirPods Pro 2 (USB-C)",
            }
            if len(msg_data) >= 2:
                model_id = (msg_data[0] << 8) | msg_data[1]
                model = device_models.get(model_id, f"Audio Device (0x{model_id:04X})")
                details.append(model)
            else:
                details.append("AirPods / Audio Device")
        elif msg_type == 0x09:  # AirPlay Target
            details.append("AirPlay Target (Apple TV/HomePod)")
        elif msg_type == 0x0C:  # Handoff
            details.append("Handoff Active")
        elif msg_type == 0x0F:  # Nearby Action
            if len(msg_data) >= 1:
                action = APPLE_NEARBY_ACTIONS.get(msg_data[0], f"Action 0x{msg_data[0]:02X}")
                details.append(f"Nearby Action: {action}")
            else:
                details.append("Nearby Action")
        elif msg_type == 0x16:  # AirPods Pairing
            details.append("AirPods/Beats (Pairing Mode)")
        elif msg_type == 0x02 or msg_type == 0x05:
            details.append("AirDrop")
        else:
            details.append(type_name)

        offset += 2 + msg_len

    return " | ".join(details) if details else None


def get_manufacturer_name(company_id: int) -> str:
    """Look up the manufacturer name from company ID."""
    return COMPANY_IDENTIFIERS.get(company_id, f"Unknown (ID: 0x{company_id:04X})")


def device_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    """Callback for each discovered device (live scanning)."""
    name = device.name or "Unknown"
    rssi = advertisement_data.rssi
    print(f"  Found: {name:<20} | {device.address} | RSSI: {rssi} dBm")


def get_device_manufacturer(adv_data: AdvertisementData) -> tuple[int, str]:
    """Extract manufacturer ID and name from advertisement data."""
    if adv_data.manufacturer_data:
        company_id = next(iter(adv_data.manufacturer_data.keys()))
        return company_id, get_manufacturer_name(company_id)
    return 0xFFFF, "Unknown"


def print_device(address: str, device: BLEDevice, adv_data: AdvertisementData, verbose: bool = False):
    """Print device information."""
    name = device.name or "Unknown"
    rssi = adv_data.rssi
    manufacturer = adv_data.manufacturer_data
    services = adv_data.service_uuids

    print(f"Device: {name}")
    print(f"  Address: {address}")
    print(f"  RSSI: {rssi} dBm")

    if manufacturer:
        for company_id, data in manufacturer.items():
            manufacturer_name = get_manufacturer_name(company_id)
            print(f"  Manufacturer: {manufacturer_name} (0x{company_id:04X})")

            # Decode Apple-specific advertising
            if company_id == 0x004C:  # Apple
                apple_info = decode_apple_advertising(data)
                if apple_info:
                    print(f"  Apple Type: {apple_info}")

            if verbose:
                print(f"  Raw Data: {data.hex()}")

    if services:
        print(f"  Services: {', '.join(services)}")

    print()


async def scan_devices(
    timeout: float = 10.0,
    filter_name: str = None,
    live: bool = False,
    sort_by: str = "rssi",
    group_by_manufacturer: bool = False,
    verbose: bool = False
):
    """
    Scan for BLE devices.

    Args:
        timeout: Scan duration in seconds
        filter_name: Optional filter for device names (case-insensitive)
        live: If True, print devices as they are found
        sort_by: Sort by 'rssi', 'name', or 'manufacturer'
        group_by_manufacturer: If True, group devices by manufacturer
        verbose: If True, show raw manufacturer data
    """
    print(f"Scanning for BLE devices ({timeout} seconds)...")
    print("-" * 60)

    if live:
        scanner = BleakScanner(detection_callback=device_callback)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()
        devices = scanner.discovered_devices_and_advertisement_data
    else:
        devices = await BleakScanner.discover(timeout=timeout, return_adv=True)

    print("-" * 60)

    # Convert to list and apply filter
    device_list = []
    for address, (device, adv_data) in devices.items():
        name = device.name or "Unknown"
        if filter_name and filter_name.lower() not in name.lower():
            continue
        device_list.append((address, device, adv_data))

    print(f"\nFound {len(device_list)} device(s):\n")

    if group_by_manufacturer:
        # Group by manufacturer
        from collections import defaultdict
        groups = defaultdict(list)

        for address, device, adv_data in device_list:
            _, manufacturer_name = get_device_manufacturer(adv_data)
            groups[manufacturer_name].append((address, device, adv_data))

        # Sort groups by name, but put "Unknown" last
        sorted_groups = sorted(
            groups.items(),
            key=lambda x: (x[0] == "Unknown", x[0])
        )

        for manufacturer_name, group_devices in sorted_groups:
            print("=" * 60)
            print(f" {manufacturer_name} ({len(group_devices)} devices)")
            print("=" * 60)

            # Sort devices within group by RSSI
            group_devices.sort(
                key=lambda x: x[2].rssi if x[2].rssi else -100,
                reverse=True
            )

            for address, device, adv_data in group_devices:
                print_device(address, device, adv_data, verbose)
    else:
        # Sort devices
        if sort_by == "rssi":
            device_list.sort(
                key=lambda x: x[2].rssi if x[2].rssi else -100,
                reverse=True
            )
        elif sort_by == "name":
            device_list.sort(
                key=lambda x: (x[1].name or "zzz").lower()
            )
        elif sort_by == "manufacturer":
            device_list.sort(
                key=lambda x: get_device_manufacturer(x[2])[1].lower()
            )

        for address, device, adv_data in device_list:
            print_device(address, device, adv_data, verbose)


def main():
    parser = argparse.ArgumentParser(description="Scan for BLE devices")
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=10.0,
        help="Scan timeout in seconds (default: 10)"
    )
    parser.add_argument(
        "--filter", "-f",
        type=str,
        default=None,
        help="Filter devices by name (case-insensitive)"
    )
    parser.add_argument(
        "--live", "-l",
        action="store_true",
        help="Show devices as they are found"
    )
    parser.add_argument(
        "--sort", "-s",
        type=str,
        choices=["rssi", "name", "manufacturer"],
        default="rssi",
        help="Sort by: rssi (signal strength), name, or manufacturer (default: rssi)"
    )
    parser.add_argument(
        "--group", "-g",
        action="store_true",
        help="Group devices by manufacturer"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show raw manufacturer data"
    )

    args = parser.parse_args()

    asyncio.run(scan_devices(
        timeout=args.timeout,
        filter_name=args.filter,
        live=args.live,
        sort_by=args.sort,
        group_by_manufacturer=args.group,
        verbose=args.verbose
    ))


if __name__ == "__main__":
    main()
