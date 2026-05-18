from machine import Pin ,ADC, I2C, SoftI2C
import time
import scd4x

# - - - CONFIGURE LE PORT SUR LE SHIELD - - -
def config_port_scd(pin_sda,pin_scl,port):
    i2c = I2C(port, sda=pin_sda, scl=pin_scl, freq=100000)   # RaspberryPi pico sur le port I2C1 
    scd = scd4x.SCD4X(i2c)   # Initialisation de la librairie
    return scd  # retourne l'objet initialisé issu de la classe scd4x

#fonction pour mettre à jour les paramètres du capteur il faut faire très attention de ne pas appeller cette fonction trop souvent (2000 fois max dans la vie du capteur)
#fonction pour mettre à jour les paramètres du capteur
def change_parametres(capteur, temp, alt):
    print(" Arrêt des mesures pour modifier les paramètres...")
    capteur.stop_periodic_measurement()
    time.sleep(0.5) # Pause obligatoire pour que le capteur passe en mode "repos"
    
    try:
        capteur.altitude = alt
        capteur.temperature_offset = temp
        capteur.persist_settings()  # Stocke les parametres dans la mémoire permanente 
        print(" Nouveaux paramètres (Offset) sauvegardés !")
    except Exception as e:
        print(" Erreur pendant l'écriture des paramètres :", e)
        
    time.sleep(0.5)
    capteur.start_periodic_measurement() # On relance les mesures

#fonction de prise de mesures
def obtenir_donnees(capteur):
    if capteur.data_ready:
        temperature = capteur.temperature
        relative_humidity = capteur.relative_humidity
        co2_ppm_level = capteur.CO2
        return co2_ppm_level,temperature,relative_humidity

#fonction pour recalibrer le capteur
def recalibration(capteur, cible_co2):
    print(f" Arrêt des mesures pour calibration forcée à {cible_co2} ppm...")
    capteur.stop_periodic_measurement()
    time.sleep(0.5) # Pause obligatoire pour le capteur
    
    try:
        # La commande exacte dépend de ta librairie scd4x, mais c'est souvent celle-ci :
        capteur.force_calibration(cible_co2) 
        print(" Calibration réussie !")
    except Exception as e:
        print(" Erreur pendant la calibration :", e)
        
    time.sleep(0.5)
    capteur.start_periodic_measurement() # On relance la machine