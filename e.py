import os
import time
import random

PISOS = 5

RESET = "\033[0m"
AZUL = "\033[1;34m"
AMARILLO = "\033[1;33m"
VERDE = "\033[1;32m"

def dibujar_ascensor(piso_actual):
    """ Dibuja la posición actual del ascensor """
    os.system('clear' if os.name == 'posix' else 'cls')

    for i in range(PISOS, 0, -1):
        if i == piso_actual:
            print(f"{AZUL} [ ]  |  Piso {i} {RESET}")
        else:
            print(f"      |  Piso {i}")

def simular_ascensor(inicio, fin):
    """ Simula el movimiento del ascensor """
    paso = 1 if inicio < fin else -1

    for piso in range(inicio, fin + paso, paso):
        dibujar_ascensor(piso)

        if paso == 1:
            print(f"{AMARILLO}\nEl elevador está subiendo...\n{RESET}")
        else:
            print(f"{AMARILLO}\nEl elevador está bajando...\n{RESET}")
        
        time.sleep(0.8) 

    print(f"{VERDE}\nEl elevador ha llegado al piso {fin} :D!\n{RESET}")

def main():
    random.seed()  

    piso_inicio = random.randint(1, PISOS)
    piso_fin = piso_inicio
    while piso_fin == piso_inicio:
        piso_fin = random.randint(1, PISOS)

    simular_ascensor(piso_inicio, piso_fin)

if __name__ == "__main__":
    main()