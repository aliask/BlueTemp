import sys
import asyncio
import logging
import struct

logger = logging.getLogger(__name__)

from bleak import BleakClient

ADDRESS = "A4:C1:38:29:F2:91"
TEMPERATURE_CHARACTERISTIC_UUID = "00002a1f-0000-1000-8000-00805f9b34fb"


async def main(address):
    async with BleakClient(address, timeout=15.0) as client:
        logger.info(f"Connected: {client.is_connected}")
        value = bytes(await client.read_gatt_char(TEMPERATURE_CHARACTERISTIC_UUID))
        temperature = struct.unpack("H", value)[0] / 10
        print(f"Temp: {temperature:.1f} °C")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))
