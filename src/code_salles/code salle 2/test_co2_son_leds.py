import time
import math
from machine import Pin

# Import de tes librairies locales
from lib_scd4x import config_port_scd, obtenir_donnees
from lib_led import config_led, indicateur_visuel, piloter_led
from lib_son import config_port_son, niveau_sonore

# --- CONFIGURATION MATÉRIEL ---
SEUIL_CO2_OK = 800.0         
SEUIL_CO2_ALERTE = 1500.0
SEUIL_BRUIT_ALERTE = 2000   # À ajuster en regardant la console !

PIN_SDA = 8
PIN_SCL = 9
PORT_SCD = 0

NUM_LEDS = 6        
PIN_DATA = 1        
PIN_CLOCK = 0       
BRIGHTNESS = 0.1    

PIN_SON = 26

# --- INITIALISATION ---
print("Initialisation du matériel...")
strip = config_led(NUM_LEDS, PIN_DATA, PIN_CLOCK, BRIGHTNESS)
micro = config_port_son(PIN_SON)
scd = config_port_scd(PIN_SDA, PIN_SCL, PORT_SCD)

print("Démarrage du capteur CO2...")
scd.stop_periodic_measurement()
time.sleep(1)
scd.start_periodic_measurement()

print("\n🚀 Boucle de test ultra-rapide démarrée !")
print("-" * 50)

# Variables de mémorisation
co2_actuel = 0
dernier_affichage_bruit = time.ticks_ms()

while True:
    try:
        # 1. Lecture du Bruit (prend environ 50ms avec ta nouvelle fonction lib_son)
        bruit_brut = niveau_sonore(micro)

        # 2. Lecture du CO2 (Instantané : retourne les données QUE si elles sont prêtes)
        mesure = obtenir_donnees(scd)
        if mesure:
            co2_actuel, temp, hum = mesure
            
            # On met à jour les LEDs normalement (seulement s'il n'y a pas d'alerte bruit en cours)
            if bruit_brut <= SEUIL_BRUIT_ALERTE:
                indicateur_visuel(co2_actuel, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)
        
        # 3. Affichage du bruit 1 fois par seconde (pour t'aider à calibrer sans spammer la console)
        if time.ticks_diff(time.ticks_ms(), dernier_affichage_bruit) > 1000:
            print(f"Bruit Brut actuel: {bruit_brut} (Alerte si > {SEUIL_BRUIT_ALERTE})")
            dernier_affichage_bruit = time.ticks_ms()

        # 4. GESTION DE L'ALERTE SONORE (Prioritaire et très réactive)
        if bruit_brut > SEUIL_BRUIT_ALERTE:
            print(f"🔊 ---> DÉPASSEMENT DU BRUIT ({bruit_brut}) ! Clignotement...")
            
            # Fait clignoter 4 fois en gardant la couleur actuelle du CO2
            for _ in range(4): 
                if co2_actuel > 0:
                    indicateur_visuel(co2_actuel, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)
                time.sleep(0.1) 
                
                piloter_led(0, strip) # On éteint
                time.sleep(0.1)
            
            # On rallume après le clignotement avec la bonne couleur
            if co2_actuel > 0:
                indicateur_visuel(co2_actuel, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)

        # 5. Toute petite pause pour ne pas saturer le processeur
        time.sleep(0.05)

    except Exception as e:
        print("Erreur pendant la boucle :", e)
        time.sleep(2)