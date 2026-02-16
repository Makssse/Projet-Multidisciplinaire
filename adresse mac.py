import network
import time
from machine import Pin, SPI

def connect_ethernet():
    # Configuration des broches SPI pour le W5500 (standard Waveshare)
    # Vérifie ton manuel si les pins diffèrent, mais c'est le standard :
    spi = SPI(0, 2_000_000, mosi=Pin(19), miso=Pin(16), sck=Pin(18))
    nic = network.WIZNET5K(spi, Pin(17), Pin(20)) # (spi, cs, reset)
    
    nic.active(True)
    
    # 1. Récupérer l'adresse MAC
    import ubinascii
    mac = ubinascii.hexlify(nic.config('mac'),':').decode()
    print(f"Adresse MAC : {mac}")

    # 2. Tentative de connexion DHCP pour l'IP
    print("Activation de l'interface Ethernet...")
    
    # Attente de l'attribution IP par le routeur
    timeout = 10
    while not nic.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        
    if nic.isconnected():
        print("Connecté au réseau !")
        print(f"Configuration IP : {nic.ifconfig()[0]}")
    else:
        print("Échec DHCP : Vérifie ton câble RJ45 !")

connect_ethernet()