import machine
import time

# --- CLASS SK9822 SIMPLIFIÉE ---
class DotStar:
    def __init__(self, data_pin, clock_pin, num_leds, brightness=0.5):
        self.num_leds = num_leds
        self.brightness = brightness
        # On utilise SoftSPI pour pouvoir choisir n'importe quel pin facilement
        self.spi = machine.SoftSPI(baudrate=1000000, sck=machine.Pin(clock_pin), mosi=machine.Pin(data_pin), miso=machine.Pin(12)) # Miso n'est pas utilisé
        self.pixels = [(0, 0, 0)] * num_leds
        
        # Frame de début (32 bits de 0)
        self.start_frame = b'\x00\x00\x00\x00'
        # Frame de fin (32 bits de 1)
        self.end_frame = b'\xFF\xFF\xFF\xFF'

    def set_pixel(self, i, r, g, b):
        if 0 <= i < self.num_leds:
            self.pixels[i] = (r, g, b)

    def show(self):
        # Préparer le buffer
        data = bytearray(self.start_frame)
        
        # Le header de chaque LED commence par 111 (brillance) + 5 bits de luminosité globale
        bright_val = int(31 * self.brightness) | 0xE0
        
        for r, g, b in self.pixels:
            data.append(bright_val)
            data.append(b) # SK9822 est souvent en ordre BGR
            data.append(g)
            data.append(r)
            
        data.extend(self.end_frame)
        self.spi.write(data)

    def fill(self, r, g, b):
        for i in range(self.num_leds):
            self.set_pixel(i, r, g, b)
        self.show()

    def clear(self):
        self.fill(0, 0, 0)
