from machine import Pin,ADC, I2C, SoftI2C
import time
from lib_scd4x import *
from lib_led import *

# - - - Parametres SCD40 - - - #
CO2_sda = 6
CO2_scl = 7 
CO2_port = 1
CO2_ppm = 400
scd = config_port_scd(CO2_sda,CO2_scl,CO2_port)

# - - - Parametres LEDs - - - #
strip = config_led()



# - - - Code continu - - - #
scd.start_periodic_measurement()

time.sleep(8)
while True:
    CO2_ppm = obtenir_donnees(scd)
    indicateur_visuel(CO2_ppm, strip)


