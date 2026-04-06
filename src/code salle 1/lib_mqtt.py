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
        self.callback = None # Pour stocker la fonction de réception

    def _encode_str(self, s):
        return struct.pack("!H", len(s)) + s

    def connecter(self):
        try:
            addr = socket.getaddrinfo(self.broker, self.port)[0][-1]
            self.sock = socket.socket()
            self.sock.connect(addr)
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

    # --- NOUVELLES FONCTIONS POUR L'INTERRUPTEUR ---

    def set_callback(self, f):
        """ Définit la fonction à appeler lors d'un message """
        self.callback = f

    def subscribe(self, topic):
        """ S'abonne à un sujet MQTT """
        topic_b = topic.encode() if isinstance(topic, str) else topic
        payload = struct.pack("!H", 1) + self._encode_str(topic_b) + b"\x00"
        self.sock.write(b"\x82" + bytes([len(payload)]) + payload)

    def check_msg(self):
        """ Vérifie si un message est arrivé de manière précise """
        self.sock.setblocking(False)
        try:
            # 1. On lit juste le premier octet (Type de paquet)
            res = self.sock.read(1)
            if res:
                # 0x30 est le code pour un message "PUBLISH"
                if res[0] & 0xf0 == 0x30: 
                    # 2. On lit la taille restante (1 octet pour les petits messages)
                    remaining_length = self.sock.read(1)[0]
                    # 3. On lit tout le reste du paquet d'un coup
                    data = self.sock.read(remaining_length)
                    
                    # 4. On extrait le topic (les 2 premiers octets indiquent sa taille)
                    topic_len = struct.unpack("!H", data[:2])[0]
                    topic = data[2:2+topic_len].decode()
                    # 5. Le reste est le message (payload)
                    msg = data[2+topic_len:].decode()
                    
                    if self.callback:
                        self.callback(topic, msg)
        except Exception as e:
            # Souvent une erreur "EAGAIN" si rien n'est prêt, c'est normal
            pass
        finally:
            self.sock.setblocking(True)

def connecter_ethernet(ip, mac_str):
    spi = SPI(0, baudrate=20_000_000, mosi=Pin(19), miso=Pin(16), sck=Pin(18))
    rst = Pin(20, Pin.OUT)
    rst.value(0)
    time.sleep_ms(100)
    rst.value(1)
    time.sleep_ms(200)
    nic = network.WIZNET5K(spi, Pin(17), Pin(20))
    nic.active(True)
    nic.ifconfig((ip, "255.255.255.0", "10.40.1.1", "10.40.1.1"))
    while not nic.isconnected():
        time.sleep_ms(500)
    return nic