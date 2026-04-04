from machine import Pin ,ADC, I2C, SoftI2C
import time
import scd4x

# - - - CONFIGURE LE PORT SUR LE SHIELD - - -
def config_port_scd(pin_sda,pin_scl,port):
    i2c = I2C(port, sda=pin_sda, scl=pin_scl, freq=100000)   # RaspberryPi pico sur le port I2C1 
    scd = scd4x.SCD4X(i2c)   # Initialisation de la librairie
    return scd  # retourne l'objet initialisé issu de la classe scd4x


def change_parametres(capteur,temp,alt):
    capteur.altitude = alt
    capteur.temperature_offset = temp
    capteur.persist_settings()  # Stocke les parametres dans la mémoire permanente 



def obtenir_donnees(capteur):
    if capteur.data_ready:
        temperature = capteur.temperature
        relative_humidity = capteur.relative_humidity
        co2_ppm_level = capteur.CO2
        return co2_ppm_level,temperature,relative_humidity



