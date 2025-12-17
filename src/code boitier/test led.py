import machine
import time
from Led import *

# --- CONFIGURATION ---
NUM_LEDS = 10         # Nombre de LEDs sur ta bande
PIN_DATA = 18        #green (data)
PIN_CLOCK = 19        #blue (clok)
#gnd : yellow ; vcc : red
BRIGHTNESS = 0.3      # Luminosité (0.1 à 1.0) - Attention aux yeux !

# Initialisation
strip = DotStar(PIN_DATA, PIN_CLOCK, NUM_LEDS, BRIGHTNESS)

print("Test des couleurs...")

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
    for i in range(NUM_LEDS):
        strip.set_pixel(i, 255, 0, 255) # Violet
        strip.show()
        time.sleep(0.1)
        strip.set_pixel(i, 0, 0, 0) # Eteindre après