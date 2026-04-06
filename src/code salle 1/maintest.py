#code pour la pi pico de la salle 1
import time
from machine import WDT, Pin 

time.sleep(1)
led = Pin("LED", Pin.OUT)
for _ in range(10): # Clignote très vite 10 fois
    led.value(1); time.sleep(0.05)
    led.value(0); time.sleep(0.05)

import uasyncio as asyncio
import ujson
import sys

# 1. Dossier des librairies
#sys.path.append('/src/code salle 1/lib')

from lib_scd4x import *
from lib_led import *
from lib_mqtt import *
from lib_son import config_port_son, niveau_sonore
from lib_IP_MAC import connect_ethernet

SALLE_ID = "salle1" # A CHANGER SELON PICO c'est la seule ligne à changer exemple : salle2

#on récupère l'IP et l'adresse MAC de la pico 
mac_pico, ip_pico = connect_ethernet()
print(f"mac = {mac_pico}")
print(f"ip = {ip_pico}")

# --- ÉTAT DU SYSTÈME
systeme_actif = True  # Le système démarre "Allumé" par défaut

# --- CONFIGURATION MQTT
IP_PICO = ip_pico  
MAC_PICO = mac_pico 
BROKER_IP = "10.40.1.20"
MQTT_USER = "reseau_co2"      # Minuscule comme dans ton test
MQTT_PASS = "co2_saintpaul"  # Ton mot de passe qui fonctionne
INTERVALLE_MQTT = 5         # Envoi toutes les 10 secondes sur HA pour commencer
SEUIL_CO2_OK = 800.0         #seuil pour les ppm du CO2
SEUIL_CO2_ALERTE = 1500.0
#CIBLE_CALIBRATION_CO2 = 400.0

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

def reception_message(topic, msg):
    """ Cette fonction s'exécute dès qu'un message MQTT arrive """
    global systeme_actif
    # On s'assure que 'msg' est bien une chaîne de caractères propre
    if isinstance(msg, bytes):
        ordre = msg.decode().strip()
    else:
        ordre = str(msg).strip()
        
    print(f"📩 Ordre reçu : [{ordre}] sur le topic [{topic}]")

    if "OFF" in ordre:
        systeme_actif = False
        print("💤 Système mis en PAUSE")
    elif "ON" in ordre:
        systeme_actif = True
        print("🚀 Système RÉVEILLÉ")
    elif "recalibrer" in ordre:
        #recalibration(scd, CIBLE_CALIBRATION_CO2)
        return 0



async def tache_leds_et_capteur(scd, strip, micro, wdt):
    while True:
        wdt.feed()  # On nourrit toujours le chien de garde
        
        if systeme_actif:
            try:
                mesure = obtenir_donnees(scd)
                if mesure:
                    co2, temp, hum = mesure
                    donnees_actuelles["co2"] = co2
                    donnees_actuelles["temp"] = round(temp, 1)
                    donnees_actuelles["humi"] = round(hum, 1)
                    donnees_actuelles["bruit"] = niveau_sonore(micro)
                    indicateur_visuel(co2, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE) 
            except Exception as e:
                print("Erreur lecture capteur:", e)
        else:
            # Si le système est éteint : on éteint physiquement les LEDs
            piloter_led(0, strip)
        
        await asyncio.sleep(5)

async def tache_mqtt(mqtt, wdt):
    # 1. On dit au client MQTT quelle fonction utiliser pour les messages reçus
    mqtt.set_callback(reception_message)
    while True:
        try:
            if mqtt.sock is None:
                print(f"Connexion au Broker...")
                if mqtt.connecter():
                    # 2. TRÈS IMPORTANT : S'abonner au topic de l'interrupteur
                    mqtt.subscribe(f"ecole/{SALLE_ID}/set_status")
                    mqtt.publier(f"ecole/{SALLE_ID}/availability", "online", retain=True)
            
            if mqtt.sock:
                # 3. On vérifie si Home Assistant a envoyé un message (ON ou OFF)
                mqtt.check_msg()
                
                # 4. On n'envoie les stats que si le système est actif
                if systeme_actif:
                    payload = ujson.dumps(donnees_actuelles)
                    mqtt.publier(f"ecole/{SALLE_ID}/state", payload) #
                    print(f"Données envoyées : {payload}")
                
        except Exception as e:
            print("Erreur MQTT:", e)

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
    print("\n--- DETECTIVE ERREUR ---")
    # Cette ligne affiche le fichier et la ligne exacte
    sys.print_exception(e) 
    print("------------------------\n")