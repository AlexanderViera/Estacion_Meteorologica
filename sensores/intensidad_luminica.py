from machine import Pin, I2C
import time

class SensorLuz:
    def __init__(self, sda_pin=0, scl_pin=1, freq=400000):
        # Como dejo flotando ADDR, la dirección será 0x23. MANDAR ADDR A MASA DESPUES
        self.address = 0x23
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        
        # 0x10 es el comando para "Medición continua de alta resolución (1 Lux)"
        self.modo_continuo = 0x10 
        
        # Le enviamos el comando de arranque
        try:
            self.i2c.writeto(self.address, bytes([self.modo_continuo]))
            # El manual pide esperar al menos 120ms para la primera medición
            time.sleep_ms(150) 
        except OSError:
            print("Error: No se encontró el BH1750. Revisá cables SDA/SCL y el pin ADDR.")

    def leer_lux(self):
        """Devuelve la intensidad lumínica en Lux"""
        try:
            # El sensor devuelve exactamente 2 bytes con el valor de la luz
            data = self.i2c.readfrom(self.address, 2)
            
            # Matemática de la hoja de datos: 
            # Combinamos los dos bytes y los dividimos por 1.2
            lux = ((data[0] << 8) | data[1]) / 1.2
            return round(lux, 1)
            
        except OSError:
            return None