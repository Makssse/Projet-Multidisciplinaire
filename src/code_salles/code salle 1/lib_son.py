from machine import Pin,ADC
import time


def config_port_son(PIN_SON):
    capteur_son = ADC(PIN_SON) #le port A0 du shield est en analog INPUT et s'appelle capteur_son
    return capteur_son

def niveau_sonore( capteur_son):
    value = capteur_son.read_u16()   # on lit une valeur entre 0 et 65535 pour capteur_son
    return value