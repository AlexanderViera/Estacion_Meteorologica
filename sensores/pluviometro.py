from machine import Pin
import time

class Pluviometro:
    def __init__(self, pin_num, mm_por_basculacion=0.3):
        # Como usás resistencia física externa, configuramos solo como entrada
        self.pin = Pin(pin_num, Pin.IN)
        self.mm_por_basculacion = mm_por_basculacion
        
        self.contador_pulsos = 0
        self.ultimo_pulso_ms = 0
        
        # Dispara cuando el imán junta los contactos y el voltaje sube a 3.3V (RISING)
        self.pin.irq(trigger=Pin.IRQ_RISING, handler=self._isr_basculacion)

    def _isr_basculacion(self, pin):
        # Esta es la Rutina de Servicio de Interrupción (ISR).
        # Debe ser extremadamente corta y rápida.
        
        tiempo_actual = time.ticks_ms()
        
        # Debouncing por software: Ignoramos cualquier pulso que ocurra 
        # en menos de 100 milisegundos desde el pulso anterior.
        if time.ticks_diff(tiempo_actual, self.ultimo_pulso_ms) > 100:
            self.contador_pulsos += 1
            self.ultimo_pulso_ms = tiempo_actual

    def leer_lluvia_mm(self):
        # Retorna el acumulado en milímetros reales
        return self.contador_pulsos * self.mm_por_basculacion