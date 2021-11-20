#!/usr/bin/env python3

import asyncio
import logging
import sys

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from pyzabbix import ZabbixMetric, ZabbixSender

from sensor_data import SensorData

logger = logging.getLogger(__name__)

ATC_MAC_PREFIX = "A4:C1:38"
ENV_SERVICE = "0000181a-0000-1000-8000-00805f9b34fb"


def send_data_to_zabbix(data: SensorData, sensorname: str):
    packet = [
        ZabbixMetric("Environment", f"temperature[{sensorname}]", data.temperature),
        ZabbixMetric("Environment", f"humidity[{sensorname}]", data.humidity),
        ZabbixMetric("Environment", f"battery[{sensorname}]", data.battery_pct),
    ]
    result = ZabbixSender(use_config=True).send(packet)
    logger.debug(result)


def ble_advertisement_cb(device: BLEDevice, ad_data: AdvertisementData):
    if (
        device.address.startswith(ATC_MAC_PREFIX)
        and ENV_SERVICE in ad_data.service_data
    ):
        raw_data = ad_data.service_data[ENV_SERVICE]
        if len(raw_data) == 15:
            data = SensorData.from_custom_format(raw_data[6:])
        elif len(raw_data) == 13:
            data = SensorData.from_atc1441_format(raw_data[6:])
        else:
            logger.warning(f"Unexpected data format: {hex(ad_data.service_data)}")
            return
        display_name = device.name if device.name else device.address
        logger.info(
            f"{display_name}@{device.rssi} dBM: {data.temperature:.2f} °C, {data.humidity:.2f}%, {data.battery_mv}mv ({data.battery_pct}%)"
        )
        try:
            send_data_to_zabbix(data, display_name)
        except Exception as e:
            logger.warning(f"Failure while sending to Zabbix: {str(e)}")
    else:
        logger.debug(f"Advertisement from {device.address}: {ad_data}")


async def main():
    scanner = BleakScanner()
    scanner.register_detection_callback(ble_advertisement_cb)

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
