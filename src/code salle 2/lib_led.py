import machine
import time
from Led import *

# --- CONFIGURATION ---
def config_led(NUM_LEDS,PIN_DATA,PIN_CLOCK,BRIGHTNESS):
    LED_STRIP = DotStar(PIN_DATA, PIN_CLOCK, NUM_LEDS, BRIGHTNESS)
    return LED_STRIP

def indicateur_visuel(CO2_ppm,bandeau, SEUIL_CO2_OK, SEUIL_CO2_ALERTE):
    if CO2_ppm<SEUIL_CO2_OK:
        bandeau.fill(0,255,0)
    
    if SEUIL_CO2_OK<=CO2_ppm<=SEUIL_CO2_ALERTE:
        bandeau.fill(255,127,0) 

    if CO2_ppm>SEUIL_CO2_ALERTE:
        bandeau.fill(255,0,0)



