import sys
import time

# 1. Ajout du chemin des librairies (si elles sont dans ce dossier)
sys.path.append('/src/code boitier')

# 2. Importation des fonctions de ta lib
try:
    from lib_son import config_port_son, niveau_sonore
    print("✅ Bibliothèque lib_son chargée.")
except ImportError:
    print("❌ Erreur : lib_son.py est introuvable.")
    sys.exit()

# 3. Initialisation du matériel
# Note : Ta lib utilise Pin 25 (LED) et ADC 26 (Port A0) par défaut
led_interne, micro = config_port_son(26) 
print("🚀 Test du capteur de son lancé sur A0...")

# 4. Boucle de lecture
while True:
    try:
        # Cette fonction lit le son, l'affiche, et fait clignoter la LED
        niveau_sonore(led_interne, micro)
        
    except KeyboardInterrupt:
        print("\nTest arrêté.")
        break
    except Exception as e:
        print(f"Erreur : {e}")
        time.sleep(1)