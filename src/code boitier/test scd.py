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


'''
### Configuration I2C
i2c_interface = 1

sdapin = Pin(14) # Pins utilisées pour communiquer avec le capteur de CO2
sclpin = Pin(15)


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
