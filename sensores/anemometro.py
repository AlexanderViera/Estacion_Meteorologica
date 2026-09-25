from machine import Pin
from time import ticks_us, ticks_diff
import uasyncio as asyncio


class sensor_velocidad:
    # Constantes según datasheet del anemómetro:
    # V(mph) = P * (2.25 / T)   [P = pulsos, T = periodo en segundos]
    PULSOS_A_MPH = 2.25
    MPH_A_MS = 0.44704

    def __init__(self, pin_num, trigger):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)

        self.contador = 0
        self.tstart = ticks_us()
        self.delta = 0

    async def wait_edge(self):
        """Tarea que cuenta los pulsos de fondo"""
        while True:
            await self.flag.wait()
            diferencia = ticks_diff(ticks_us(), self.tstart)

            # Filtro anti-rebote
            if diferencia > 10000 or self.contador == 0:
                self.delta += diferencia
                self.tstart = ticks_us()
                self.contador += 1

    def leer_velocidad(self):
        """Calcula la velocidad actual en m/s y resetea contadores"""
        velocidad = 0.0

        # Verificación de viento detenido: si pasaron más de 3 segundos desde el último pulso
        if ticks_diff(ticks_us(), self.tstart) > 3000000:
            velocidad = 0.0
        elif self.contador > 1:
            # Frecuencia = Pulsos / Segundos transcurridos
            frecuencia_hz = 1000000 * self.contador / self.delta
            mph = frecuencia_hz * self.PULSOS_A_MPH   # fórmula del datasheet
            velocidad = round(mph * self.MPH_A_MS, 2)  # mph -> m/s

        # Reseteo para el próximo ciclo
        self.delta = 0
        self.contador = 0

        return velocidad