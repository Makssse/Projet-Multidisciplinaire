from machine import Pin ,ADC, I2C, SoftI2C
import time
import scd4x


i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=100000)   # RaspberryPi pico example

scd = scd4x.SCD4X(i2c)
print(scd)
scd.start_periodic_measurement()  # start_low_periodic_measurement() is a lower power alternative


if scd.data_ready:
    temperature = scd.temperature
    print(temperature)
    relative_humidity = scd.relative_humidity
    co2_ppm_level = scd.CO2
