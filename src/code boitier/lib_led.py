import machine
import time
from Led import *

# --- CONFIGURATION ---
def config_led():
    NUM_LEDS = 6          # Nombre de LEDs sur ta bande
    PIN_DATA = 18         #green (data)
    PIN_CLOCK = 19        #blue (clock)
    BRIGHTNESS = 0.3      # Luminosité (0.1 à 1.0) - Attention aux yeux !

    # Initialisation
    LED_STRIP = DotStar(PIN_DATA, PIN_CLOCK, NUM_LEDS, BRIGHTNESS)

    return LED_STRIP, NUM_LEDS

def indicateur_visuel(CO2_ppm,bandeau):
    if CO2_ppm<800.0:
        bandeau.fill(0,255,0)
    
    if 800.0<=CO2_ppm<=1500.0:
        bandeau.fill(255,127,0)

    if CO2_ppm>1500.0:
        bandeau.fill(0,123,200)



strip, nb_led = config_led()



"""print("Test des couleurs...")

while True:
    # Rouge
    strip.fill(0, 123, 200)
    time.sleep(1)
    
    # Vert
    strip.fill(0, 255, 0)
    time.sleep(1)
    
    # Bleu
    strip.fill(0, 0, 255)
    time.sleep(1)
    
    # Animation chenillard
    strip.clear()
    for i in range(nb_led):
        strip.set_pixel(i, 255, 0, 255) # Violet
        strip.show()
        time.sleep(0.1)
        strip.set_pixel(i, 0, 0, 0) # Eteindre après"""