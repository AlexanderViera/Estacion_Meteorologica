from machine import Pin, Timer
from time import ticks_us, ticks_diff
import uasyncio as asyncio

class AsyncPin:
    contador = 0
    tstart = ticks_us()
    delta = 0

    def __init__(self, pin, trigger):
        self.pin = pin
        self.flag = asyncio.ThreadSafeFlag()
        self.pin.irq(handler=lambda pin: self.flag.set(), trigger=trigger)

    async def wait_edge(self):
        await self.flag.wait()
        diferencia = ticks_diff(ticks_us(), self.tstart)
        if diferencia > 100 or self.contador == 0:
            # print('Got edge.')
            self.delta += diferencia
            self.tstart = ticks_us()
            self.contador += 1

pin_in = Pin(22, Pin.IN, Pin.PULL_DOWN)
async_pin = AsyncPin(pin_in, Pin.IRQ_RISING)

async def waiting():
    while True:
        await async_pin.wait_edge()

asyncio.create_task(waiting())

async def calculo_velocidad():
    velocidad = 0
    while True:
        if async_pin.contador > 1:
            velocidad = round(1000000*(async_pin.contador)/async_pin.delta,1)
            async_pin.delta = 0
            async_pin.contador = 0
        elif async_pin.delta > 6000000:
            velocidad = 0
            async_pin.delta = 0
            async_pin.contador = 0
        print(velocidad)


#await client.publish("meteorologica/", datos, qos = 1)