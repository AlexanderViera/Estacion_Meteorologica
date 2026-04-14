from xmlrpc import client
from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
from sensores.temp_hum_presion import SensorAmbiente
from sensores.anemometro import AsyncPin  # <--- IMPORTAMOS TU CLASE
from machine import Pin

# ==========================================
# 1. FUNCIONES
# ==========================================
async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

async def conn_han(client):
    # Por ahora no nos suscribimos a nada, pero la función debe existir
    pass 

def sub_cb(topic, msg, retained):
    # Esta función maneja los mensajes que llegan. La dejamos lista por las dudas.
    print(f"Recibido en {topic.decode()}: {msg.decode()}")


# ==========================================
# 2. BUCLE PRINCIPAL
# ==========================================
async def main(client):
    await client.connect() # Obliga a conectar antes de continuar
    await asyncio.sleep(2) # Esperamos a que el broker procese la conexión
    
    # Creamos el objeto del sensor
    estacion_clima = SensorAmbiente(sda_pin=14, scl_pin=15)
    anemometro = AsyncPin(22, Pin.IRQ_RISING) # <--- INSTANCIAMOS ANEMÓMETRO

    asyncio.create_task(anemometro.wait_edge())
    

    while True:
        # 1. Adquisición
        temp, pres, hum = estacion_clima.leer_todo()
        vel = anemometro.leer_velocidad()

        
        # 2. Verificación y Publicación
        if temp is not None:
            await client.publish('estacion/temperatura', f"{temp:.2f}", qos=1)
            await client.publish('estacion/presion', f"{pres:.2f}", qos=1)
            await client.publish('estacion/humedad', f"{hum:.2f}", qos=1)

            await client.publish('estacion/viento', f"{vel:.1f}", qos=1)

            print(f"Publicado -> Temp: {temp:.2f}°C | Pres: {pres:.2f} hPa | Hum: {hum:.2f}% | Vel: {vel:.1f} Hz/s")
        else:
            print("Esperando lectura válida del BME280...")
            
        # 3. Pausa operativa
        await asyncio.sleep(20)

    
    # 2. LANZAMOS LA TAREA DE CONTEO EN SEGUNDO PLANO
    # Esto se queda escuchando los pulsos del pin 22 todo el tiempo
        
        # --- Publicación ---
        if temp is not None:
            await client.publish('estacion/temperatura', f"{temp:.2f}", qos=1)
            await client.publish('estacion/presion', f"{pres:.2f}", qos=1)
            await client.publish('estacion/humedad', f"{hum:.2f}", qos=1)
            # Publicamos la velocidad
            await client.publish('estacion/viento', f"{vel:.1f}", qos=1)
            
            print(f"Publicado -> Temp: {temp:.2f}°C | Viento: {vel:.1f} Hz/s")
        else:
            print("Error en sensores...")
            
        await asyncio.sleep(20)


# ==========================================
# 3. CONFIGURACIÓN Y ARRANQUE
# ==========================================
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['subs_cb'] = sub_cb

# IMPORTANTE: Cambiá esto a True si usas un broker online (ej. HiveMQ/Adafruit)
# o dejalo en False si es un broker local en red (ej. Mosquitto sin encriptar)
config['ssl'] = True

MQTTClient.DEBUG = True  
client = MQTTClient(config)

# Toma de control de la Raspberry Pi Pico
try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()

