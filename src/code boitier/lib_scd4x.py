from machine import Pin ,ADC, I2C, SoftI2C
import time
import scd4x

# - - - CONFIGURE LE PORT SUR LE SHIELD - - -
def config_port_scd(pin_sda,pin_scl,port):
    i2c = I2C(port, sda=pin_sda, scl=pin_scl, freq=100000)   # RaspberryPi pico sur le port I2C1 
    scd = scd4x.SCD4X(i2c)   # Initialisation de la librairie
    print(scd)
    return scd  # retourne l'objet initialisé issu de la classe scd4x


def change_parametres(capteur,temp,alt):
    capteur.altitude = alt
    capteur.temperature_offset = temp
    capteur.persist_settings()  # Stocke les parametres dans la mémoire permanente 



def obtenir_donnees(capteur):
    if capteur.data_ready:
        temperature = capteur.temperature
        print(temperature)
        relative_humidity = capteur.relative_humidity
        print(relative_humidity)
        co2_ppm_level = capteur.CO2
        print(co2_ppm_level)
        return co2_ppm_level



'''
### Configuration I2C
i2c_interface = 1

sdapin = Pin(6) # Pins utilisées pour communiquer avec le capteur de CO2
sclpin = Pin(7)


i2c = I2C(i2c_interface, scl=sclpin, sda=sdapin, freq=100000)

# Scan la Raspberry pour voir les appareils I2C connectés
i2cdevices = i2c.scan()
print(i2cdevices)
if len(i2cdevices) == 0:
 print("pas d'appareil i2c !")
else:
 print('appareils i2c trouvés:',len(i2cdevices))
for device in i2cdevices:
 print("A l'adresse: ",hex(device))


scd40adress = hex(0x62)
buf = hex(0xe4b8) 
i2c.write(scd40adress,buf, stop=True)
time(20)
data_ready = i2c.readfrom(scd40adress,128, stop=True)
print(data_ready)
#data = i2c.readfrom(scd40adress, 128, True)
'''
