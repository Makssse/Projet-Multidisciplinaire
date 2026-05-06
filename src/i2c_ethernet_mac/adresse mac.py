import network
from machine import Pin, SPI
import time

def connect_ethernet():
    # Force le reset matériel
    eth_reset = Pin(20, Pin.OUT)
    eth_reset.value(0) # On éteint la puce
    time.sleep(0.1)
    eth_reset.value(1) # On la rallume
    time.sleep(0.5)    # On attend qu'elle finisse de booter

    # 2. Configuration SPI (On peut monter à 20MHz pour plus de perf)
    spi = SPI(0, 20_000_000, mosi=Pin(19), miso=Pin(16), sck=Pin(18))
    
    # 3. Initialisation du contrôleur WIZNET5K
    # CS=17, Reset=20 (géré manuellement au dessus), mais on le passe au driver
    nic = network.WIZNET5K(spi, Pin(17), Pin(20)) 
    
    nic.active(True)
    
    # Affichage de la MAC pour vérification
    import ubinascii
    mac = ubinascii.hexlify(nic.config('mac'),':').decode()
    print(f"--- Ethernet Debug ---")
    print(f"Adresse MAC : {mac}")

    # 4. Tentative DHCP
    print("En attente d'une IP (DHCP)...")
    
    timeout = 15
    while not nic.isconnected() and timeout > 0:
        # On vérifie l'état du lien physique (0: pas de câble, 1: câble ok)
        status = nic.status() 
        time.sleep(1)
        timeout -= 1
        print(f"Tentative... (reste {timeout}s)")
        
    if nic.isconnected():
        print("\n[SUCCÈS] Connecté au réseau !")
        print(f"Configuration IP : {nic.ifconfig()[0]}")
    else:
        print("\n[ÉCHEC] Le DHCP n'a pas répondu.")
        print("1_ Vérifie que ton câble est bien relié à un switch/box.")
        print("2_ Teste une IP Statique.")


connect_ethernet()