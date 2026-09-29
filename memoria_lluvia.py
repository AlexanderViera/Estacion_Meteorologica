import os

ARCHIVO = 'lluvia_acumulada.txt'

def guardar_lluvia(valor):
    try:
        # 'w' sobreescribe el valor anterior
        with open(ARCHIVO, 'w') as f:
            f.write(str(valor))
    except Exception as e:
        print(f"Error al escribir en flash: {e}")

def leer_lluvia():
    try:
        with open(ARCHIVO, 'r') as f:
            contenido = f.read()
            return float(contenido) if contenido else 0.0
    except OSError:
        # Si el archivo no existe devuelve 0
        return 0.0