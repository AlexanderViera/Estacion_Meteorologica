from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import json
from sensores.temp_hum_presion import SensorAmbiente
from sensores.anemometro import sensor_velocidad
from sensores.intensidad_luminica import SensorLuz
from sensores.veleta import Veleta
from sensores.pluviometro import Pluviometro
from sensores.bateria import MedidorBateria
from memoria_lluvia import guardar_lluvia, leer_lluvia
from interfaz import BotonReset, LedEstado
from machine import Pin, I2C, WDT
import machine

# ==========================================
# FUNCIONES
# ==========================================
async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep(1)

async def conn_han(client):
    pass 

def sub_cb(topic, msg, retained):
    # Esta función maneja los mensajes que llegan.
    print(f"Recibido en {topic.decode()}: {msg.decode()}")

async def aviso_watchdog(wdt):
    """Alimenta al perro guardián cada 5 segundos. Si uasyncio se cuelga, esto falla y la placa se reinicia."""
    while True:
        wdt.feed()
        await asyncio.sleep(5)


async def bucle_sensores(client, estacion_clima, anemometro, luxometro, veleta, pluviometro, monitor_ups):
    while True:
        # Leer todos los sensores
        temp, pres, hum = estacion_clima.leer_todo()
        vel = anemometro.leer_velocidad()
        luz = luxometro.leer_lux()
        direccion = await veleta.leer_direccion()
        lluvia_acumulada = pluviometro.leer_lluvia_mm()

        # Lectura de la batería
        tension = monitor_ups.leer_tension()
        payload_bat = None
        if tension is not None:
            datos_mantenimiento = {
                "voltaje_bateria": tension,
                "estado": "descargando" if tension < 3.5 else "operativo"
            }
            payload_bat = json.dumps(datos_mantenimiento)

        # Redondear valores y preparar JSON
        temp_val = round(temp, 2) if temp is not None else None
        pres_val = round(pres, 2) if pres is not None else None
        hum_val = round(hum, 2) if hum is not None else None
        vel_val = round(vel, 1) if vel is not None else None
        luz_val = round(luz*2.36, 1) if luz is not None else None
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
        payload_bat = json.dumps(datos_mantenimiento)

        # Publicar en MQTT y guardar en memoria flash si falla la publicación
        if client.isconnected():
            try:
                # Publicar clima
                await client.publish('estacion/mediciones/pico', valores_json, qos=1)
                
                # Publicar batería
                if payload_bat is not None:
                    await client.publish('estacion/mantenimiento/bateria_pico', payload_bat, qos=1)
                
                guardar_lluvia(lluvia_acumulada)
                print(f"Publicado OK: {valores_json}")
            except Exception as e:
                print(f"Fallo al publicar, guardando en local: {e}")
                guardar_lluvia(lluvia_acumulada)
        else:
            print("Sin conexión a Internet. Guardando lluvia en memoria Flash.")
            guardar_lluvia(lluvia_acumulada)
            
        await asyncio.sleep(300)
        print("\n")

# ==========================================
# BUCLE PRINCIPAL
# ==========================================

async def main(client):
    # INICIALIZAR WATCHDOG DE HARDWARE (8 segundos de límite)
    wdt = WDT(timeout=8000)
    asyncio.create_task(aviso_watchdog(wdt))

    # INICIALIZAR SENSORES
    i2c_bus = I2C(1, sda=Pin(14), scl=Pin(15), freq=400000)
    estacion_clima = SensorAmbiente(i2c_bus)
    anemometro = sensor_velocidad(22, Pin.IRQ_RISING)
    luxometro = SensorLuz(i2c_bus)
    veleta = Veleta(26)
    pluviometro = Pluviometro(pin_num=21, mm_por_basculacion=0.3)
    monitor_ups = MedidorBateria(pin=27)

    # ------------------------- PARTE INTERFAZ -----------------------------------
    boton_reinicio = BotonReset(pin_num=7)
    led_power = LedEstado(pin_num=6)
    led_wifi = LedEstado(pin_num=5)

    asyncio.create_task(led_power.rutear_parpadeo(lambda: True))
    asyncio.create_task(led_wifi.rutear_parpadeo(lambda: client.isconnected()))

    # ----------------------------------------------------------------------------

    # RECUPERAR LLUVIA OFFLINE
    lluvia_guardada = leer_lluvia()
    pluviometro.restaurar_memoria(lluvia_guardada)

    asyncio.create_task(anemometro.wait_edge())
    
    
    # LANZAR EL BUCLE DE SENSORES EN SEGUNDO PLANO
    asyncio.create_task(bucle_sensores(client, estacion_clima, anemometro, luxometro, veleta, pluviometro, monitor_ups))

    # GESTIÓN DE CONEXIÓN (El bucle principal solo observa la conexión a la red)
    tiempo_sin_conexion = 0
    LIMITE_DESCONEXION = 900  # 900 segundos = 15 minutos
    while True:
        try:
            if not client.isconnected():
                print("Intentando conectar al broker MQTT...")
                await client.connect()
            else:
                # Si estamos conectados, reseteamos el contador
                tiempo_sin_conexion = 0
        except Exception as e:
            print(f"Error de conexión: {e}. Reintentando...")

        # Si después de intentar conectar seguimos offline, sumamos tiempo
        if not client.isconnected():
            tiempo_sin_conexion += 10
            print(f"Sin conexión. Tiempo acumulado: {tiempo_sin_conexion}/{LIMITE_DESCONEXION} segs.")
            
            # Evaluar condición del Watchdog Lógico
            if tiempo_sin_conexion >= LIMITE_DESCONEXION:
                print("\n[CRÍTICO] Tiempo límite de desconexión superado.")
                print("Posible Livelock del chip Wi-Fi. Forzando Hard Reset...\n")
                await asyncio.sleep(1) # Pausa para que se imprima el mensaje en consola
                machine.reset() # Reinicio físico total
        
        # Revisa el estado de la conexión cada 10 segundos
        await asyncio.sleep(10)



# ==========================================
# CONFIGURACIÓN Y ARRANQUE
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

