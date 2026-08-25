from machine import Pin, I2C
from lib.bme280 import BME280 # Importamos la librería que descargaste

class SensorAmbiente:
    def __init__(self, i2c_bus):
        self.i2c = i2c_bus
        
        try:
            self.sensor = BME280(i2c=self.i2c, address=0x76)
            print("BME280 inicializado correctamente.")
        except Exception as e:
            print(f"Error al encontrar el BME280: {e}")

    def leer_todo(self):
        """Devuelve una tupla con (temperatura, presión, humedad)"""
        try:
            # La librería devuelve strings con unidades (ej: '25.5C')
            # Algunos métodos devuelven valores numéricos según la versión
            t, p, h = self.sensor.read_compensated_data()
            
            # Procesamos para tener números limpios
            # temperatura = t / 100.0
            # presion = p / 256.0 / 100.0 # Convertimos a hPa
            # humedad = h / 1024.0
            temperatura = t
            presion = p / 100.0 # Convertimos a hPa
            humedad = h
            
            return temperatura, presion, humedad
        except:
            return None, None, None
        