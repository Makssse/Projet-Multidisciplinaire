from machine import Pin, ADC
import time

def config_port_son(PIN_SON):
    capteur_son = ADC(PIN_SON) 
    return capteur_son

def niveau_sonore(capteur_son):
    # On écoute pendant 50 millisecondes pour capter les "pics" de l'onde sonore
    max_val = 0
    min_val = 65535
    start = time.ticks_ms()
    
    while time.ticks_diff(time.ticks_ms(), start) < 50:
        val = capteur_son.read_u16()
        if val > max_val: max_val = val
        if val < min_val: min_val = val
        
    # L'amplitude (le volume réel) est l'écart entre le max et le min
    amplitude = max_val - min_val
    return amplitude