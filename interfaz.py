from machine import Pin
import machine
import uasyncio as asyncio
import time

class BotonReset:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.IN)
        self.ultimo_pulso = 0
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=self.isr_reset)

    def isr_reset(self, pin):
        ahora = time.ticks_ms()
        
        if time.ticks_diff(ahora, self.ultimo_pulso) > 10:
            self.ultimo_pulso = ahora
            print("\n[!] BOTÓN PRESIONADO: Reiniciando sistema en 1 segundo...\n")
            time.sleep(1)
            machine.reset() # Aca se ejecuta el hard-reset

class LedEstado:
    def __init__(self, pin_num):
        self.pin = Pin(pin_num, Pin.OUT)
        self.apagar()

    def encender(self):
        self.pin.value(0)

    def apagar(self):
        self.pin.value(1)

    async def rutear_parpadeo(self, condicion_func):
        while True:
            if condicion_func():
                self.encender()
                await asyncio.sleep(0.5)  # Tiempo encendido
                self.apagar()
                await asyncio.sleep(3.0)  # Tiempo apagado
            else:
                self.apagar()
                await asyncio.sleep(0.5)