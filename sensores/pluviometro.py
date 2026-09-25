from machine import Pin
import time

class Pluviometro:
    def __init__(self, pin_num, mm_por_basculacion=0.3):
        self.pin = Pin(pin_num, Pin.IN)
        self.mm_por_basculacion = mm_por_basculacion
        
        self.contador_pulsos = 0
        self.ultimo_pulso_ms = 0
        
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=self._isr_basculacion)

    def _isr_basculacion(self, pin):
        
        tiempo_actual = time.ticks_ms()
        
        if time.ticks_diff(tiempo_actual, self.ultimo_pulso_ms) > 100:
            self.contador_pulsos += 1
            self.ultimo_pulso_ms = tiempo_actual

    def leer_lluvia_mm(self):
        return self.contador_pulsos * self.mm_por_basculacion