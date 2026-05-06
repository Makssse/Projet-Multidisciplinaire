import uasyncio as asyncio
import ujson
import sys
import time

# 1. Chemin vers vos librairies
sys.path.append('/src/code boitier')

# On n'importe QUE la partie réseau/MQTT
from lib_mqtt import MQTTClient, connecter_ethernet

# --- CONFIGURATION (Identique à votre réseau) ---
SALLE_ID = "salle1"
IP_PICO = "10.40.1.22"
BROKER_IP = "10.40.1.20"
MQTT_USER = "reseau_co2"
MQTT_PASS = "co2_saintpaul" # <--- Mettez votre vrai mot de passe ici !

async def main():
    print("--- TEST RÉSEAU UNIQUEMENT (SANS CAPTEUR) ---")
    
    # 2. Initialisation Ethernet
    print(f"Connexion Ethernet en cours sur {IP_PICO}...")
    try:
        connecter_ethernet(IP_PICO, "DE:AD:BE:EF:00:01")
        print("Ethernet initialisé (Vérifiez le clignotement orange !)")
    except Exception as e:
        print(f"Erreur Ethernet : {e}")

    # 3. Configuration MQTT
    mqtt = MQTTClient(f"pico_{SALLE_ID}", BROKER_IP, 1883, MQTT_USER, MQTT_PASS)

    while True:
        try:
            # Tentative de connexion au Broker
            if mqtt.sock is None:
                print(f"Tentative de connexion au Broker {BROKER_IP}...")
                if mqtt.connecter():
                    print("✅ CONNECTÉ à Home Assistant !")
            
            if mqtt.sock:
                # On crée des données "bidon" pour le test
                donnees_test = {
                    "co2": 555, 
                    "temp": 22.5, 
                    "humi": 40.0
                }
                payload = ujson.dumps(donnees_test)
                
                # Envoi du paquet
                mqtt.publier(f"ecole/{SALLE_ID}/state", payload)
                print(f"🚀 Message de test envoyé : {payload}")
                
        except Exception as e:
            print(f"❌ Erreur MQTT : {e}")

        # On attend 10 secondes entre chaque envoi pour le test
        await asyncio.sleep(10)

# Lancement du script
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Test arrêté par l'utilisateur.")