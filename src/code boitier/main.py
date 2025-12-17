from machine import Pin,ADC, I2C, SoftI2C
import time

led = Pin(25, Pin.OUT) #la pin 25 est appellé led et est en mode OUT

capteur_son = ADC(26) #le port A0 du shield est en analog INPUT et s'appelle capteur_son

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

while True:
    value = capteur_son.read_u16()   # on lit une valeur entre 0 et 65535 pour capteur_son
    print("Niveau sonore :", value)
    time.sleep(1)

    led.on() #or led.value(1)
    time.sleep(1) 
    led.off()
    time.sleep(1)
