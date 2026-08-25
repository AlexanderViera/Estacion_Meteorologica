from machine import ADC, Pin
import uasyncio as asyncio

class Veleta:
    def __init__(self, pin):
        # Inicializamos el pin ADC
        self.pin = ADC(Pin(pin))
        
    async def leer_direccion(self):
        await asyncio.sleep(0)  # Cede control al scheduler de uasyncio
        valor_adc = self.pin.read_u16()
        
        # Mapeo matemático lineal: (Valor leído * Máximo de grados) / Valor máximo del ADC
        grados = (valor_adc * 360) // 65535
        
        # Detalle de ingeniería: 360° y 0° representan ambos el Norte exacto. 
        # Es convención normalizar el 360 a 0 para mantener el rango de 0 a 359.
        if grados == 360:
            grados = 0
            
        return grados