from machine import Pin
from time import ticks_us, ticks_diff
import uasyncio as asyncio

class sensor_velocidad:
    def __init__(self, pin_num, trigger, factor_m_s=0.447):
        # Como usás resistencia física de pull-down externa, Pin.IN puro es más limpio
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)
        
        self.factor_m_s = factor_m_s  # Constante del fabricante (ej: 0.666 m/s por Hz)
        self.contador = 0
        self.tstart = ticks_us()
        self.delta = 0

    async def wait_edge(self):
        """Tarea que cuenta los pulsos de fondo"""
        while True:
            await self.flag.wait()
            diferencia = ticks_diff(ticks_us(), self.tstart)
            
            # Filtro anti-rebote: 15000 microsegundos = 15 ms
            if diferencia > 15000 or self.contador == 0:
                self.delta += diferencia
                self.tstart = ticks_us()
                self.contador += 1

    def leer_velocidad(self):
        """Calcula la velocidad actual en m/s y resetea contadores"""
        velocidad = 0.0
        
        # Verificación de viento detenido: Si pasaron más de 3 segundos (3M us) desde el último pulso
        if ticks_diff(ticks_us(), self.tstart) > 3000000:
            velocidad = 0.0
        elif self.contador > 1:
            # Frecuencia = Pulsos / Segundos transcurridos
            frecuencia_hz = 1000000 * self.contador / self.delta
            velocidad = round(frecuencia_hz * self.factor_m_s, 1)
        
        # Reseteo obligatorio para el próximo ciclo
        self.delta = 0
        self.contador = 0
        
        return velocidad