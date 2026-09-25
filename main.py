from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import json
from sensores.temp_hum_presion import SensorAmbiente
from sensores.anemometro import sensor_velocidad
from sensores.intensidad_luminica import SensorLuz
from sensores.veleta import Veleta
from sensores.pluviometro import Pluviometro
from machine import Pin, I2C

# ==========================================
# 1. FUNCIONES
# ==========================================
async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

async def conn_han(client):
    pass 

def sub_cb(topic, msg, retained):
    # Esta función maneja los mensajes que llegan.
    print(f"Recibido en {topic.decode()}: {msg.decode()}")


# ==========================================
# 2. BUCLE PRINCIPAL
# ==========================================
async def main(client):
    await client.connect() # Obliga a conectar antes de continuar
    await asyncio.sleep(2) # Esperamos a que el broker procese la conexión

    i2c_bus = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
    
    # Creamos el objeto del sensor
    estacion_clima = SensorAmbiente(i2c_bus)
    anemometro = sensor_velocidad(22, Pin.IRQ_RISING)
    luxometro = SensorLuz(i2c_bus)
    veleta = Veleta(26)
    pluviometro = Pluviometro(pin_num=21, mm_por_basculacion=0.3)

    asyncio.create_task(anemometro.wait_edge())
    #asyncio.create_task(veleta.leer_direccion())  # <--- INICIO TAREA DE VELETA
    

    while True:
        # Adquisición
        temp, pres, hum = estacion_clima.leer_todo()
        vel = anemometro.leer_velocidad()
        luz = luxometro.leer_lux()
        direccion = await veleta.leer_direccion()
        lluvia_acumulada = pluviometro.leer_lluvia_mm()

        temp_val = round(temp, 2) if temp is not None else None
        pres_val = round(pres, 2) if pres is not None else None
        hum_val = round(hum, 2) if hum is not None else None
        vel_val = round(vel, 1) if vel is not None else None
        luz_val = round(luz, 1) if luz is not None else None
        luz_val = luz_val*2.36;
        #vel_val = vel_val*10;
        #luz_val = 10000;
        valores_dict = {
            "temperatura": temp_val,
            "presion": pres_val,
            "humedad": hum_val,
            "lux": luz_val,
            "viento_velocidad": vel_val,
            "viento_direccion_grados": direccion,
            "cantidad_lluvia": round(lluvia_acumulada, 2)
        }

        valores_json = json.dumps(valores_dict)
        print(f"Paquete generado: {valores_json}")

        
        # Verificación y Publicación
        if temp is not None:
            #await client.publish('estacion/temperatura', f"{temp:.2f} °C", qos=1)
            #await client.publish('estacion/presion', f"{pres:.2f} hPa", qos=1)
            #await client.publish('estacion/humedad', f"{hum:.2f}%", qos=1)
            print(f"Publicado -> Temp: {temp:.2f}°C | Pres: {pres:.2f} hPa | Hum: {hum:.2f}% | Vel: {vel:.1f} m/s")
        else:
            print("Esperando lectura válida del BME280...")

        if luz is not None:
            print(f"Publicado -> Luz: {luz:.1f} Lux")
            #await client.publish('estacion/luz', f"{luz:.1f} Lux", qos=1)
        else:
            print("No se pudo leer la intensidad lumínica")

        print(f"Publicado -> Dirección del viento: {direccion}")

        #await client.publish('estacion/viento', f"{vel:.1f} m/s", qos=1)
        #await client.publish('estacion/direccion', direccion, qos=1)

        
            
        await client.publish('estacion/mediciones/pico', valores_json, qos=1)
        #await client.publish('estacion/mediciones/#', valores_json, qos=1)
        await asyncio.sleep(2)
        print("\n")



# ==========================================
# 3. CONFIGURACIÓN Y ARRANQUE
# ==========================================
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['subs_cb'] = sub_cb

config['ssl'] = True

MQTTClient.DEBUG = True  
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()

