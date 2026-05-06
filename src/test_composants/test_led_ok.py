import sys
import time

NUM_LEDS = 6        # Nombre de LEDs sur ta bande
PIN_DATA = 1        #green (data)
PIN_CLOCK = 0       #blue (clock)
BRIGHTNESS = 0.1    # Luminosité (0.1 à 1.0)

# 2. Importation des fonctions de ta lib
try:
    from lib_led import config_led, indicateur_visuel
    print("✅ Bibliothèque lib_led chargée.")
except ImportError:
    # Si config_port_led n'existe pas, on utilise config_led de ton fichier
    from lib_led import config_led, indicateur_visuel
    config_port_led = config_led

# 3. Initialisation du bandeau

bandeau = config_led(NUM_LEDS,PIN_DATA,PIN_CLOCK,BRIGHTNESS)

print(f"🚀 Test du bandeau ({NUM_LEDS} LEDs) lancé...")

def test_couleurs():
    # Simulation du niveau VERT (< 800 ppm)
    print("Test : Niveau de CO2 faible (VERT)")
    indicateur_visuel(400, bandeau, 800, 1500)
    time.sleep(2)

    # Simulation du niveau ORANGE (800 - 1500 ppm)
    print("Test : Niveau de CO2 moyen (ORANGE)")
    indicateur_visuel(900, bandeau, 800, 1500)
    time.sleep(2)

    # Simulation du niveau BLEU (> 1500 ppm)
    # Note : Ta lib met du bleu (0,123,200) pour le niveau haut
    print("Test : Niveau de CO2 élevé (BLEU)")
    indicateur_visuel(1600, bandeau, 800, 1500)
    time.sleep(2)

    # Extinction (optionnel, pour vérifier la fin)
    print("Test terminé, extinction...")
    bandeau.fill(0, 0, 0)
    time.sleep(1)

# Lancement du cycle de test
while True:
    test_couleurs()