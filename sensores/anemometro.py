from machine import Pin
from time import ticks_us, ticks_diff
import uasyncio as asyncio

class AsyncPin:
    def __init__(self, pin_num, trigger):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)
        
        # Atributos de instancia (con self para que no se mezclen)
        self.contador = 0
        self.tstart = ticks_us()
        self.delta = 0

    async def wait_edge(self):
        """Tarea que cuenta los pulsos de fondo"""
        while True:
            await self.flag.wait()
            diferencia = ticks_diff(ticks_us(), self.tstart)
            if diferencia > 100 or self.contador == 0:
                self.delta += diferencia
                self.tstart = ticks_us()
                self.contador += 1

    def leer_velocidad(self):
        """Calcula la velocidad actual y resetea contadores"""
        velocidad = 0
        if self.contador > 1:
            velocidad = round(1000000 * (self.contador) / self.delta, 1)
        elif self.delta > 6000000:
            velocidad = 0
        
        # IMPORTANTE: Reseteamos para la próxima lectura del main
        self.delta = 0
        self.contador = 0
        return velocidad