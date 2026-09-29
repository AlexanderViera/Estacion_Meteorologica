from machine import ADC, Pin

class MedidorBateria:
    def __init__(self, pin, r1=10000, r2=10000):
        self.adc = ADC(Pin(pin))
        self.factor_divisor = (r1 + r2) / r2
        self.voltaje_referencia = 3.3

    def leer_tension(self):
        try:
            valor_crudo = self.adc.read_u16()
            voltaje_pin = (valor_crudo * self.voltaje_referencia) / 65535.0
            voltaje_real = voltaje_pin * self.factor_divisor
            
            return round(voltaje_real, 2)
        except Exception as e:
            print(f"Error leyendo batería: {e}")
            return None