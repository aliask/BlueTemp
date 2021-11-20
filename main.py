import asyncio
import logging
import struct
import sys

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

logger = logging.getLogger(__name__)

ATC_MAC_PREFIX = "A4:C1:38"
ENV_SERVICE = "0000181a-0000-1000-8000-00805f9b34fb"


class SensorData(object):
    temperature: float = 0.0
    humidity: float = 0.0
    battery_mv: int = 0
    battery_pct: int = 0

    def __init__(self, temperature, humidity, battery_mv, battery_pct):
        self.temperature = temperature
        self.humidity = humidity
        self.battery_mv = battery_mv
        self.battery_pct = battery_pct

    @classmethod
    def from_custom_format(cls, sensordata: bytes):
        (temp_01, hum_01, batt_mv, batt_pct, counter, flags) = struct.unpack(
            "hHHBBB", sensordata
        )
        temp = temp_01 / 100
        hum = hum_01 / 100
        return cls(temp, hum, batt_mv, batt_pct)

    @classmethod
    def from_atc1441_format(cls, sensordata: bytes):
        (temp, hum, batt_pct, batt_mv, counter) = struct.unpack("hBBHB", sensordata)
        return cls(temp, hum, batt_mv, batt_pct)


def simple_callback(device: BLEDevice, advertisement_data: AdvertisementData):
    if (
        device.address.startswith(ATC_MAC_PREFIX)
        and ENV_SERVICE in advertisement_data.service_data
    ):
        raw_data = advertisement_data.service_data[ENV_SERVICE]
        if len(raw_data) == 15:
            data = SensorData.from_custom_format(raw_data[6:])
        elif len(raw_data) == 13:
            data = SensorData.from_atc1441_format(raw_data[6:])
        else:
            logger.warning(
                f"Unexpected data format: {hex(advertisement_data.service_data)}"
            )
            return
        display_name = device.name if device.name else device.address
        logger.info(
            f"{display_name}@{device.rssi} dBM: {data.temperature:.2f} °C, {data.humidity:.2f}%, {data.battery_mv}mv ({data.battery_pct}%)"
        )
    else:
        logger.debug(f"CRAP FROM {device.address}: {advertisement_data}")


async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(simple_callback)

    while True:
        await scanner.start()
        await asyncio.sleep(5.0)
        await scanner.stop()


if __name__ == "__main__":
    logger.setLevel(level=logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s)",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    asyncio.run(main())
