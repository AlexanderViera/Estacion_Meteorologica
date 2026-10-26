from machine import Pin
from time import ticks_us, ticks_diff
import uasyncio as asyncio


class sensor_velocidad:
    # Hoja de datos del anemómetro: V(mph) = f(Hz) * 2.25
    PULSOS_A_MPH = 2.25
    MPH_A_MS = 0.44704

    def __init__(self, pin_num, trigger):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)

        self.contador = 0
        self.tstart = ticks_us()      # último pulso aceptado (antirrebote)
        self.t_ventana = ticks_us()   # inicio de la ventana de medición

    async def wait_edge(self):
        """Tarea que cuenta los pulsos de fondo"""
        while True:
            await self.flag.wait()
            ahora = ticks_us()
            # Filtro antirrebote: descarta pulsos a menos de 10 ms del anterior
            if ticks_diff(ahora, self.tstart) > 10000 or self.contador == 0:
                self.tstart = ahora
                self.contador += 1

    def leer_velocidad(self):
        """Velocidad media (m/s) desde la última lectura; reinicia la ventana"""
        ahora = ticks_us()
        ventana = ticks_diff(ahora, self.t_ventana)
        velocidad = 0.0
        if self.contador > 0 and ventana > 0:
            frecuencia_hz = 1000000 * self.contador / ventana
            velocidad = round(frecuencia_hz * self.PULSOS_A_MPH * self.MPH_A_MS, 2)
        self.contador = 0
        self.t_ventana = ahora
        return velocidad