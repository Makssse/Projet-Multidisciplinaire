import uasyncio as asyncio
import ujson
from machine import WDT, Pin
import sys
import time

# 1. Dossier des librairies
sys.path.append('/src/code boitier')

from lib_scd4x import config_port_scd, obtenir_donnees
from lib_led import config_led, indicateur_visuel
from lib_mqtt import MQTTClient, connecter_ethernet

# --- CONFIGURATION (Copiée de ton test_mqtt qui marche) ---
SALLE_ID = "salle1"
IP_PICO = "10.40.1.22"
BROKER_IP = "10.40.1.20"
MQTT_USER = "reseau_co2"      # Minuscule comme dans ton test
MQTT_PASS = "co2_saintpaul"  # Ton mot de passe qui fonctionne
INTERVALLE_MQTT = 30         # Envoi toutes les 30 secondes pour commencer

# Variables globales pour partager les données entre les tâches
donnees_actuelles = {"co2": 400, "temp": 20.0, "humi": 50.0}

async def envoyer_configuration_ha(mqtt):
    """ Envoie la configuration pour que HA crée le capteur automatiquement """
    config_topic = f"homeassistant/sensor/{SALLE_ID}_co2/config"
    payload = {
        "name": f"CO2 {SALLE_ID}",
        "state_topic": f"ecole/{SALLE_ID}/state",
        "unit_of_measurement": "ppm",
        "value_template": "{{ value_json.co2 }}",
        "device_class": "carbon_dioxide",
        "unique_id": f"pico_{SALLE_ID}_co2",
        "availability_topic": f"ecole/{SALLE_ID}/availability"
    }
    mqtt.publier(config_topic, ujson.dumps(payload), retain=True)
    print("Configuration Discovery envoyée à Home Assistant")

async def tache_leds_et_capteur(scd, strip, wdt):
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
                
                # Mise à jour des LEDs physiques
                indicateur_visuel(co2, strip)
        except Exception as e:
            print("Erreur lecture capteur:", e)
            
        await asyncio.sleep(5)

async def tache_mqtt(mqtt, wdt):
    """ Tâche lente : communication avec Home Assistant """
    configuration_envoyee = False
    
    while True:
        try:
            # Vérification de la connexion
            if mqtt.sock is None:
                print(f"Tentative de connexion au Broker {BROKER_IP}...")
                if mqtt.connecter():
                    print("✅ CONNECTÉ à Home Assistant !")
                    mqtt.publier(f"ecole/{SALLE_ID}/availability", "online", retain=True)
                    
                    if not configuration_envoyee:
                        await envoyer_configuration_ha(mqtt)
                        configuration_envoyee = True
            
            # Envoi des données réelles du capteur
            if mqtt.sock:
                payload = ujson.dumps(donnees_actuelles)
                mqtt.publier(f"ecole/{SALLE_ID}/state", payload)
                print(f"🚀 Données envoyées : {payload}")
                
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
    strip, _ = config_led()
    
    # Init Capteur avec Reset forcé pour éviter le "Working Mode"
    scd = config_port_scd(pin_sda=6, pin_scl=7, port=1)
    print("Réinitialisation du capteur...")
    scd.stop_periodic_measurement()
    time.sleep(1)
    scd.start_periodic_measurement()
    print("Capteur SCD4x prêt !")
    
    # 2. Réseau
    print(f"Initialisation Ethernet sur {IP_PICO}...")
    connecter_ethernet(IP_PICO, "DE:AD:BE:EF:00:01")
    
    # Création du client MQTT avec les bons paramètres de ton test
    mqtt = MQTTClient(f"pico_{SALLE_ID}", BROKER_IP, 1883, MQTT_USER, MQTT_PASS, 
                      will_topic=f"ecole/{SALLE_ID}/availability")

    # 3. Lancement du moteur asynchrone
    print(f"Système {SALLE_ID} opérationnel")
    await asyncio.gather(
        tache_leds_et_capteur(scd, strip, wdt),
        tache_mqtt(mqtt, wdt)
    )

# Lancement global
try:
    asyncio.run(main())
except Exception as e:
    print("Crash système fatal:", e)