import uasyncio as asyncio
import ujson
from machine import WDT, Pin

import sys
sys.path.append('/src/code boitier')

from lib_scd4x import config_port_scd, obtenir_donnees
from lib_led import config_led, indicateur_visuel
from lib_mqtt import MQTTClient, connecter_ethernet

# --- CONFIGURATION ---
SALLE_ID = "salle1"
IP_PICO = "192.168.1.101"
BROKER_IP = "192.168.1.100"
INTERVALLE_MQTT = 600  # 10 minutes

# Variables globales pour partager les données entre les tâches
donnees_actuelles = {"co2": 400, "temp": 20.0, "humi": 50.0}

async def tache_leds_et_capteur(scd, strip):
    """ Tâche rapide : mise à jour visuelle toutes les 5 secondes """
    while True:
        #wdt.feed() # On nourrit le watchdog ici aussi
        try:
            # obtenir_donnees() vérifie 'data_ready' avant de lire
            co2, temp, hum = obtenir_donnees(scd)
            if co2:
                # Mise à jour des variables globales pour la tâche MQTT
                donnees_actuelles["co2"] = co2
                donnees_actuelles["temp"] = round(temp, 1)
                donnees_actuelles["humi"] = round(hum, 1)
                
                # Mise à jour immédiate des LEDs pour les profs
                indicateur_visuel(co2, strip)
        except Exception as e:
            print("Erreur lecture capteur:", e)
            
        await asyncio.sleep(5) # Rythme calé sur le cycle du SCD40

async def tache_mqtt(mqtt, wdt):
    """ Tâche lente : envoi à Home Assistant toutes les 10 minutes """
    while True:
        # Attente de 10 minutes (découpée pour le watchdog)
        for _ in range(INTERVALLE_MQTT):
            wdt.feed()
            await asyncio.sleep(1)
            
        try:
            if mqtt.sock is None:
                if mqtt.connecter():
                    mqtt.publier(f"ecole/{SALLE_ID}/availability", "online", retain=True)
            
            if mqtt.sock:
                payload = ujson.dumps(donnees_actuelles)
                mqtt.publier(f"ecole/{SALLE_ID}/state", payload)
                print("Données envoyées à HA")
        except Exception as e:
            print("Erreur MQTT:", e)

async def main():
    # 1. Sécurité et Matériel
    #wdt = WDT(timeout=8000)
    strip, _ = config_led()
    scd = config_port_scd(pin_sda=6, pin_scl=7, port=1)
    scd.start_periodic_measurement() #
    
   # 2. Réseau
    #connecter_ethernet(IP_PICO, "DE:AD:BE:EF:00:01")
    #mqtt = MQTTClient(f"pico_{SALLE_ID}", BROKER_IP, 1883, "pico_mqtt", "mot_de_passe", 
     #                 will_topic=f"ecole/{SALLE_ID}/availability")

    # 3. Lancement des deux tâches en simultané
    print(f"Boîtier {SALLE_ID} opérationnel (LEDs 5s / MQTT 10min)")
    await asyncio.gather(
        tache_leds_et_capteur(scd, strip),
        #tache_mqtt(mqtt, wdt)
    )

# Lancement du programme
try:
    asyncio.run(main())
except Exception as e:
    print("Crash système:", e)
