import uasyncio as asyncio
from sensores.temp_hum_presion import SensorAmbiente

async def main():
    # Creamos el objeto del sensor
    estacion_clima = SensorAmbiente(sda_pin=14, scl_pin=15)

    while True:
        temp, pres, hum = estacion_clima.leer_todo()
        print(f"Temp: {temp:.2f}°C | Pres: {pres:.2f} hPa | Hum: {hum:.2f}%")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())