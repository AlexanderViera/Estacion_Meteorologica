from machine import Pin, I2C
import time

class SensorLuz:
    def __init__(self, i2c_bus):
        self.address = 0x23
        self.i2c = i2c_bus
        self.modo_continuo = 0x10 
        
        try:
            self.i2c.writeto(self.address, bytes([self.modo_continuo]))
            time.sleep_ms(150) 
            print("BH1750 inicializado correctamente.")
        except OSError:
            print("Error: No se encontró el BH1750. Revisá el bus compartido.")

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