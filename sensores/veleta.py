from machine import ADC, Pin
import uasyncio as asyncio

class Veleta:
    def __init__(self, pin):
        self.pin = ADC(Pin(pin))
        
    async def leer_direccion(self):
        await asyncio.sleep(0)
        valor_adc = self.pin.read_u16()
        
        # (Valor leído * Máximo de grados) / Valor máximo del ADC
        grados = (valor_adc * 360) // 65535
        
        if grados == 360:
            grados = 0
            
        return grados