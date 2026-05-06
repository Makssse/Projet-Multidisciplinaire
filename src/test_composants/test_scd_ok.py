import scd4x
import time
from machine import I2C, Pin

# 1. Configuration du bus I2C0 (GP8=SDA, GP9=SCL)
# On utilise une fréquence de 100kHz, standard pour le SCD40
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)

print("--- DÉMARRAGE DU TEST SCD40 ---")

try:
    # 2. Initialisation du capteur
    # L'init de la librairie appelle stop_periodic_measurement() par sécurité
    scd = scd4x.SCD4X(i2c)
    print("Capteur détecté et initialisé.")

    # 3. Lancement de la mesure périodique
    scd.start_periodic_measurement()
    print("🚀 Mesure lancée. Attente des premières données (environ 5s)...")

    # 4. Boucle de lecture infinie
    while True:
        # On vérifie si le capteur a terminé son calcul
        if scd.data_ready:
            # On récupère les trois valeurs
            co2 = scd.CO2
            temp = scd.temperature
            hum = scd.relative_humidity
            
            print("-" * 30)
            print(f"CO2  : {co2} ppm")
            print(f"Temp : {temp:.1f} °C")
            print(f"Hum  : {hum:.1f} %")
        else:
            # Si la donnée n'est pas prête, on attend un peu
            print("⏳ Capteur en cours de mesure...")
        
        # On attend 2 secondes avant de vérifier à nouveau pour ne pas saturer le bus I2C
        time.sleep(2)

except Exception as e:
    print(f"❌ Erreur : {e}")