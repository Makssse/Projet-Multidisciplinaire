#code pour la pi pico de la salle 1
import time
from machine import WDT, Pin 

time.sleep(3)
led = Pin("LED", Pin.OUT)
for _ in range(10): # Clignote très vite 10 fois
    led.value(1); time.sleep(0.05)
    led.value(0); time.sleep(0.05)

import uasyncio as asyncio
import ujson
import sys

# 1. Dossier des librairies
#sys.path.append('/src/code salle 1/lib')

from lib_scd4x import config_port_scd, obtenir_donnees
from lib_led import config_led, indicateur_visuel
from lib_mqtt import MQTTClient, connecter_ethernet
from lib_son import config_port_son, niveau_sonore

# --- CONFIGURATION MQTT
SALLE_ID = "salle1" # A CHANGER SELON PICO
IP_PICO = "10.40.1.22"   #  A CHANGER SELON PICO
MAC_PICO = "02:12:6f:54:64:9a" # A CHANGER SELON PICO
BROKER_IP = "10.40.1.20"
MQTT_USER = "reseau_co2"      # Minuscule comme dans ton test
MQTT_PASS = "co2_saintpaul"  # Ton mot de passe qui fonctionne
INTERVALLE_MQTT = 10         # Envoi toutes les 10 secondes sur HA pour commencer
SEUIL_CO2_OK = 800.0         #seuil pour les ppm du CO2
SEUIL_CO2_ALERTE = 1500.0

# CONFIGURATION MATERIEL PI PICO
#pour le capteur scd sur I2C0 de la shield
PIN_SDA = 8
PIN_SCL = 9
PORT_SCD = 0
#pour les leds, config qui fontionne pour branchement des LEDs sur UART0 ou 0,1,Vcc,GND
NUM_LEDS = 6        # Nombre de LEDs sur ta bande
PIN_DATA = 1        #green (data)
PIN_CLOCK = 0       #blue (clock)
BRIGHTNESS = 0.1    # Luminosité (0.1 à 1.0)
#pour le capteur de son
PIN_SON = 26


# Variables globales pour partager les données entre les tâches
donnees_actuelles = {"co2": 0, "temp": 0, "humi": 0, "bruit": 0}

async def tache_leds_et_capteur(scd, strip, micro, wdt):
    """ Tâche rapide : mise à jour visuelle toutes les 5 secondes """
    while True:
        wdt.feed()  # On rassure le watchdog
        try:
            mesure = obtenir_donnees(scd)
            if mesure:
                co2, temp, hum = mesure
                donnees_actuelles["co2"] = co2
                donnees_actuelles["temp"] = round(temp, 1)
                donnees_actuelles["humi"] = round(hum, 1)
                donnees_actuelles["bruit"] = niveau_sonore(micro)
                
                # Mise à jour des LEDs physiques
                indicateur_visuel(co2, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)

        except Exception as e:
            print("Erreur lecture capteur:", e)
            
        await asyncio.sleep(5)

async def tache_mqtt(mqtt, wdt):
    """ Tâche lente : communication avec Home Assistant """
    while True:
        try:
            # Vérification de la connexion
            if mqtt.sock is None:
                print(f"Tentative de connexion au Broker {BROKER_IP}...")
                if mqtt.connecter():
                    print(" CONNECTÉ à Home Assistant !")
                    mqtt.publier(f"ecole/{SALLE_ID}/availability", "online", retain=True)
            
            # Envoi des données réelles du capteur
            if mqtt.sock:
                payload = ujson.dumps(donnees_actuelles)
                mqtt.publier(f"ecole/{SALLE_ID}/state", payload)
                print(f" Données envoyées : {payload}")
                
        except Exception as e:
            print("Erreur MQTT:", e)
            configuration_envoyee = False 

        # Attente découpée pour ne pas faire rebooter le watchdog
        for _ in range(INTERVALLE_MQTT):
            wdt.feed()
            await asyncio.sleep(1)

async def main():
    # 1. Matériel et Sécurité
    wdt = WDT(timeout=8000) # Si le code freeze plus de 8s, la Pico reboot

    #init led
    strip = config_led(NUM_LEDS,PIN_DATA,PIN_CLOCK,BRIGHTNESS)

    # Init Son (Port A0 / ADC 26)
    micro = config_port_son(PIN_SON)
    
    # Init Capteur SCD avec Reset forcé pour éviter le "Working Mode"
    scd = config_port_scd(PIN_SDA, PIN_SCL, PORT_SCD)
    print("Réinitialisation du capteur")
    scd.stop_periodic_measurement()
    time.sleep(1)
    scd.start_periodic_measurement()
    print("Capteur SCD4x prêt !")
    
    # 2. Réseau
    print(f"Initialisation Ethernet sur {IP_PICO}...")
    connecter_ethernet(IP_PICO, MAC_PICO)
    
    # Création du client MQTT avec les bons paramètres de ton test
    mqtt = MQTTClient(f"pico_{SALLE_ID}", BROKER_IP, 1883, MQTT_USER, MQTT_PASS, 
                      will_topic=f"ecole/{SALLE_ID}/availability")

    # 3. Lancement du moteur asynchrone
    print(f"Système {SALLE_ID} opérationnel")
    await asyncio.gather(
        tache_leds_et_capteur(scd, strip, micro, wdt),
        tache_mqtt(mqtt, wdt)
    )

# Lancement global
try:
    asyncio.run(main())
except Exception as e:
    print("Crash système fatal:", e)