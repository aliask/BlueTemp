#!/usr/bin/env python3

import struct


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
