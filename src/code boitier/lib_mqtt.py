import time
import network
import ujson
from machine import Pin, SPI
import usocket as socket
import ustruct as struct

class MQTTClient:
    def __init__(self, client_id, broker, port, user, password, will_topic=None):
        self.client_id = client_id.encode()
        self.broker = broker
        self.port = port
        self.user = user.encode()
        self.password = password.encode()
        self.will_topic = will_topic.encode() if will_topic else None
        self.sock = None

    def _encode_str(self, s):
        return struct.pack("!H", len(s)) + s

    def connecter(self):
        try:
            addr = socket.getaddrinfo(self.broker, self.port)[0][-1]
            self.sock = socket.socket()
            self.sock.connect(addr)
            # Flags : user+password+clean session + Will
            flags = 0xC6 if self.will_topic else 0xC2
            payload = b'\x00\x04MQTT\x04' + bytes([flags]) + b'\x00\x3c'
            payload += self._encode_str(self.client_id)
            if self.will_topic:
                payload += self._encode_str(self.will_topic)
                payload += self._encode_str(b"offline")
            payload += self._encode_str(self.user)
            payload += self._encode_str(self.password)
            self.sock.write(b'\x10' + bytes([len(payload)]) + payload)
            rep = self.sock.read(4)
            return rep and rep[3] == 0
        except:
            return False

    def publier(self, topic, message, retain=False):
        try:
            topic_b = topic.encode()
            msg_b = message.encode()
            payload = self._encode_str(topic_b) + msg_b
            self.sock.write(bytes([0x31 if retain else 0x30, len(payload)]) + payload)
            return True
        except:
            self.sock = None
            return False

def connecter_ethernet(ip, mac_str):
    # --- CONFIGURATION CORRIGÉE POUR W5500-EVB-PICO ---
    # On utilise SPI(0) car les pins 16, 17, 18, 19 appartiennent au bus 0
    spi = SPI(0, baudrate=20_000_000, mosi=Pin(19), miso=Pin(16), sck=Pin(18))

    # Le Reset est souvent sur GP20 sur ces cartes
    rst = Pin(20, Pin.OUT)
    rst.value(0)
    time.sleep_ms(100)
    rst.value(1)
    time.sleep_ms(200)

    # Initialisation du contrôleur (CS=17)
    nic = network.WIZNET5K(spi, Pin(17), Pin(20)) # CS=17
    '''
        # Pins SPI standards pour W5500-EVB-Pico selon votre config
        spi = SPI(1, baudrate=20_000_000, mosi=Pin(11), miso=Pin(12), sck=Pin(10))
        rst = Pin(15, Pin.OUT)
        rst.value(0)
        time.sleep_ms(100)
        rst.value(1)
        time.sleep_ms(200)
        nic = network.WIZNET5K(spi, Pin(13), Pin(14)) # CS=13, INT=14
    '''
    nic.active(True)
    nic.ifconfig((ip, "255.255.255.0", "10.40.1.1", "10.40.1.1"))
    #nic.ifconfig((ip, "255.255.255.0", "192.168.1.1", "192.168.1.1"))
    while not nic.isconnected():
        time.sleep_ms(500)
    return nic