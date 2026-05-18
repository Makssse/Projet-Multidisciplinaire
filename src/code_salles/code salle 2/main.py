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


from lib_scd4x import *
from lib_led import *
from lib_mqtt import *
from lib_son import config_port_son, niveau_sonore
from lib_IP_MAC import connect_ethernet

SALLE_ID = "salle2" # A CHANGER SELON PICO c'est la seule ligne à changer avc IP_BROKR

#on récupère l'IP et l'adresse MAC de la pico 
mac_pico, ip_pico = connect_ethernet()
print(f"mac = {mac_pico}")
print(f"ip = {ip_pico}")

# --- ÉTAT DU SYSTÈME
systeme_actif = True  # Le système démarre "Allumé" par défaut

# --- CONFIGURATION MQTT
IP_PICO = ip_pico  
MAC_PICO = mac_pico 
BROKER_IP = "192.168.2.10" #a changer selon le réseau
MQTT_USER = "ecolesaintpaulqai"      # Minuscule comme dans ton test
MQTT_PASS = "MmeM011ier!"  # Ton mot de passe qui fonctionne
INTERVALLE_MQTT = 10         # Envoi toutes les 10 secondes sur HA pour commencer
SEUIL_CO2_OK = 1200.0         #seuil pour les ppm du CO2
SEUIL_CO2_ALERTE = 2000.0
SEUIL_BRUIT_ALERTE = 2000   # Ajuster selon la sensibilité (potentiomètre) du capteur Grove
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
BRIGHTNESS = 0.5    # Luminosité (0.1 à 1.0)

#pour le capteur de son
PIN_SON = 26

#altitude du capteur
ALTITUDE = 0


# Variables globales pour partager les données entre les tâches
donnees_actuelles = {"co2": 0, "temp": 0, "humi": 0, "bruit": 0}

def reception_message(topic, msg):
    """ Cette fonction s'exécute dès qu'un message MQTT arrive """
    global systeme_actif
    global SEUIL_CO2_ALERTE
    global SEUIL_CO2_OK
    # On s'assure que 'msg' est bien une chaîne de caractères propre
    if isinstance(msg, bytes):
        ordre = msg.decode().strip()
    else:
        ordre = str(msg).strip()
        
    print(f" Ordre reçu : [{ordre}] sur le topic [{topic}]")

    if ordre == "OFF":
        systeme_actif = False
        print(" Système mis en PAUSE")
    elif ordre == "ON":
        systeme_actif = True
        print(" Système RÉVEILLÉ")

    elif ordre.startswith("OFFSET:"):
        try:
            systeme_actif = False
            valeur = float(ordre.split(":")[1])
            print(f"Application du nouvel Offset : {valeur}°C")
            change_parametres(scd, valeur, ALTITUDE)
            systeme_actif = True
        except Exception as e:
            print("Erreur lors de l'application de l'offset:", e)
            
    elif ordre.startswith("CALIBRER:"):
        try:
            systeme_actif = False
            valeur = int(float(ordre.split(":")[1]))
            print(f"Calibration forcé à : {valeur}ppm")
            recalibration(scd, valeur)
            systeme_actif = True
        except Exception as e:
            print("Erreur lors de la calibration:", e)
    
    elif ordre.startswith("ALERTE:"):
        try:
            systeme_actif = False
            valeur = int(float(ordre.split(":")[1]))
            print(f"Seuil alerte MAJ à : {valeur}ppm")
            
            SEUIL_CO2_OK = valeur
            with open("ini.txt", "w", encoding="utf-8") as ini:
                ini.write(f"{SEUIL_CO2_OK}\n")       
                ini.write(f"{SEUIL_CO2_ALERTE}\n")

            systeme_actif = True
        except Exception as e:
            print("Erreur lors de la MAJ du seuil alerte CO2:", e)
    
    elif ordre.startswith("ALARME:"):
        try:
            systeme_actif = False
            valeur = int(float(ordre.split(":")[1]))
            print(f"Seuil alarme MAJ à : {valeur}ppm")
            
            SEUIL_CO2_ALERTE = valeur

            with open("ini.txt", "w", encoding="utf-8") as ini:
                ini.write(f"{SEUIL_CO2_OK}\n")       
                ini.write(f"{SEUIL_CO2_ALERTE}\n")

            systeme_actif = True
        except Exception as e:
            print("Erreur lors de la MAJ du seuil alarme CO2:", e)
    


async def tache_leds_et_capteur(scd, strip, micro, wdt):
    while True:
        wdt.feed()  # On nourrit toujours le chien de garde
        
        if systeme_actif:
            try:
                # 1. ÉCOUTE DU SON EN CONTINU (Très réactif)
                bruit = niveau_sonore(micro)
                donnees_actuelles["bruit"] = bruit

                
                # 2. LECTURE DU CO2 (Seulement quand il est prêt, environ toutes les 5s)
                # obtenir_donnees() ne bloque pas le code grâce à capteur.data_ready !
                mesure = obtenir_donnees(scd)
                if mesure:
                    co2, temp, hum = mesure
                    donnees_actuelles["co2"] = co2
                    donnees_actuelles["temp"] = round(temp, 1)
                    donnees_actuelles["humi"] = round(hum, 1)
                    
                    # On met à jour la couleur d'ambiance UNIQUEMENT s'il n'y a pas d'alerte bruit
                    if bruit <= SEUIL_BRUIT_ALERTE:
                        indicateur_visuel(co2, strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE) 
                
                # 3. GESTION DE L'ALERTE SONORE (Prioritaire)
                if bruit > SEUIL_BRUIT_ALERTE:
                    print(f"Alerte Bruit détectée ! Niveau: {bruit}")
                    # On fait clignoter les LEDs 4 fois avec la couleur actuelle du CO2
                    for _ in range(4): 
                        if donnees_actuelles["co2"] > 0:
                            indicateur_visuel(donnees_actuelles["co2"], strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)
                        await asyncio.sleep(0.1)
                        
                        piloter_led(0, strip) # Éteint
                        await asyncio.sleep(0.1)
                    
                    # On restaure la couleur normale après le clignotement
                    if donnees_actuelles["co2"] > 0:
                        indicateur_visuel(donnees_actuelles["co2"], strip, SEUIL_CO2_OK, SEUIL_CO2_ALERTE)

            except Exception as e:
                print("Erreur lecture capteur:", e)
        else:
            # Si le système est éteint
            piloter_led(0, strip)
        
        # 4. PAUSE TRÈS COURTE (10 vérifications du son par seconde au lieu de 1 toutes les 5s)
        await asyncio.sleep(0.1)

async def tache_mqtt(mqtt, wdt):
    # Indique client MQTT quelle fonction utiliser pour les messages reçus
    mqtt.set_callback(reception_message)
    while True:
        try:
            if mqtt.sock is None:
                print(f"Connexion au Broker...")
                if mqtt.connecter():
                    # S'abonne au topic de l'interrupteur (set_status)
                    mqtt.subscribe(f"ecole/{SALLE_ID}/set_status")
                    mqtt.publier(f"ecole/{SALLE_ID}/availability", "online", retain=True)
            
            if mqtt.sock:
                # Vérifie si Home Assistant a envoyé un message (ON ou OFF)
                mqtt.check_msg()
                
                # Envoie les stats que si le système est actif
                if systeme_actif and donnees_actuelles["co2"] > 0:
                    payload = ujson.dumps(donnees_actuelles)
                    mqtt.publier(f"ecole/{SALLE_ID}/state", payload) #
                    print(f"Données envoyées : {payload}")
                
        except Exception as e:
            print("Erreur MQTT:", e)

        for _ in range(INTERVALLE_MQTT):
            wdt.feed()
            await asyncio.sleep(1)

async def main():
    global SEUIL_CO2_OK
    global SEUIL_CO2_ALERTE
    global scd
    wdt = WDT(timeout=8000) # Si le code freeze plus de 8s, la Pico reboot

    # init led
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
    
    # Init Réseau
    print(f"Initialisation Ethernet sur {IP_PICO}...")
    connecter_ethernet(IP_PICO, MAC_PICO)
    
    # Création du client MQTT avec les bons paramètres
    mqtt = MQTTClient(f"pico_{SALLE_ID}", BROKER_IP, 1883, MQTT_USER, MQTT_PASS, 
                      will_topic=f"ecole/{SALLE_ID}/availability") #will_topic sert de testament de connexion
    
# Set-up des seuils de CO2 par les dernieres valeurs de Home Assistant
    with open("ini.txt", "r", encoding="utf-8") as ini:
        seuils=ini.readlines() 
        print(seuils)
        SEUIL_CO2_OK=int(seuils[0])
        SEUIL_CO2_ALERTE=int(seuils[1])

    # Lancement du moteur asynchrone
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