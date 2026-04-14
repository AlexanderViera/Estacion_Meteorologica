from machine import Pin, I2C
from librerias.bme280 import BME280 # Importamos la librería que descargaste

class SensorAmbiente:
    def __init__(self, sda_pin=14, scl_pin=15, freq=400000):
        # 1. Configuramos el bus I2C (usamos el canal 0 de la Pico)
        self.i2c = I2C(1, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        
        # 2. Inicializamos el sensor BME280
        # El sensor suele usar la dirección 0x76 o 0x77
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