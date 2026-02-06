from machine import Pin,ADC
import time


def config_port_son(pin):
    led = Pin(25, Pin.OUT) #la pin 25 est appellé led et est en mode OUT

    capteur_son = ADC(26) #le port A0 du shield est en analog INPUT et s'appelle capteur_son

    return led, capteur_son

def niveau_sonore(led, capteur_son):
    value = capteur_son.read_u16()   # on lit une valeur entre 0 et 65535 pour capteur_son
    print("Niveau sonore :", value)
    time.sleep(1)

    led.on() #or led.value(1)
    time.sleep(1) 
    led.off()
    time.sleep(1)