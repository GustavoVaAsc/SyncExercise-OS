import os
import time
import random
from threading import *
from collections import defaultdict

# Definir el número de pisos para la animacion inicial
PISOS = 9  # Comenzamos desde el piso 9 para la animacion (HILEVADOR)
PALABRA = "HILEVADOR"  # La palabra que se formará

# Colores
RESET = "\033[0m"
AZUL = "\033[1;34m"
VERDE = "\033[1;32m"
CYAN = "\033[1;36m"

# Función para dibujar el ascensor
def dibujarAscensor(pisoActual, palabra):
    os.system("clear")  # Limpiar la terminal

    for i in range(PISOS, 0, -1):
        if i == pisoActual:
            # Piso actual en azul
            print(f"{AZUL} [ ]  |  Piso {i} {palabra} {RESET}")
        elif i != pisoActual:
            # Pisos no utilizados en cyan
            print(f"{CYAN}      |  Piso {i}{RESET}")

# Función para simular el ascensor
def simularAscensor(inicio, fin):
    paso = 1 if inicio < fin else -1  # Determinar si sube o baja
    palabra = ""
    
    # Bajar hasta el piso 1 para formar toda la palabra
    for piso in range(inicio, fin + paso, paso):
        if len(palabra) < len(PALABRA):
            palabra += PALABRA[len(palabra)]  # Agregar una letra de la palabra
        
        dibujarAscensor(piso, palabra)

        time.sleep(0.8)  # Pausa para la animación

    print(f"{VERDE}\nHILEVADOR POR YORDI JIMENEZ Y GUSTAVO VALENZUELA!!!!\n{RESET}")
    time.sleep(2)  # Pausa para que el usuario pueda leer el mensaje

# Clase Elevador y lógica del elevador (igual que tu código original)
class Elevador:
    def __init__(self, PISOS=5):
        self.capacidad = 5
        self.piso_actual = 0
        self.direccion = 1  # 1 -- Arriba, -1 Abajo
        self.pasajeros = []  # Lista de tuplas (id_persona, piso_destino)
        self.solicitudes = defaultdict(list)  # Diccionario de piso: [personas_esperando]
        self.puerta_abierta = False
        self.PISOS = PISOS
        self.funcionando = True
        
        # Sincronizacion
        self.lock_elevador = Lock()
        self.condicion_subida = Condition(self.lock_elevador)
        self.condicion_movimiento = Condition(self.lock_elevador)
        self.semaforo_capacidad = Semaphore(self.capacidad)
        
    def detener(self):
        with self.lock_elevador:
            self.funcionando = False
            self.condicion_subida.notify_all()
            self.condicion_movimiento.notify_all()

def logicaElevador(elevador):
    while elevador.funcionando:
        with elevador.lock_elevador:
            # Verificar si hay solicitudes en el piso actual antes de abrir
            if elevador.piso_actual in elevador.solicitudes and elevador.solicitudes[elevador.piso_actual]:
                elevador.puerta_abierta = True
                print(f"\033[94m[ELEVADOR] Piso actual {elevador.piso_actual}: Puertas abiertas (solicitudes pendientes)\033[0m\n")
                time.sleep(1)
            else:
                # Verificar si hay pasajeros que quieran bajar en este piso
                pasajeros_bajando = any(piso == elevador.piso_actual for (_, piso) in elevador.pasajeros)
                if pasajeros_bajando:
                    elevador.puerta_abierta = True
                    print(f"\033[94m[ELEVADOR] Piso actual {elevador.piso_actual}: Puertas abiertas (pasajeros bajan)\033[0m\n")
                    time.sleep(1)
                else:
                    elevador.puerta_abierta = False
            
            if elevador.puerta_abierta:
                elevador.condicion_subida.notify_all()
                # Esperar tiempo de abordaje
                elevador.condicion_subida.wait(timeout=3.0)
                
                # Cerrar puertas
                elevador.puerta_abierta = False
                print(f"\033[94m[ELEVADOR] Puertas cerradas. Pasajeros: {len(elevador.pasajeros)}\033[0m\n")
                time.sleep(1)
            
            if not elevador.funcionando:
                break
            
            # Determinar siguiente piso basado en solicitudes y destinos
            proximos_pisos = []
            
            # Agregar pisos con solicitudes pendientes
            for piso, personas in elevador.solicitudes.items():
                if personas:  # Si hay personas esperando en ese piso
                    proximos_pisos.append(piso)
            
            # Agregar pisos destino de pasajeros actuales
            for (_, piso_destino) in elevador.pasajeros:
                proximos_pisos.append(piso_destino)
            
            # Si no hay solicitudes ni destinos, cambiar dirección
            if not proximos_pisos:
                if elevador.piso_actual == elevador.PISOS - 1:
                    elevador.direccion = -1
                elif elevador.piso_actual == 0:
                    elevador.direccion = 1
            else:
                # Determinar dirección basada en el piso más cercano en la dirección actual
                if elevador.direccion == 1:
                    pisos_arriba = [p for p in proximos_pisos if p > elevador.piso_actual]
                    if pisos_arriba:
                        elevador.direccion = 1
                    else:
                        elevador.direccion = -1
                else:
                    pisos_abajo = [p for p in proximos_pisos if p < elevador.piso_actual]
                    if pisos_abajo:
                        elevador.direccion = -1
                    else:
                        elevador.direccion = 1
            
            # Mover elevador
            time.sleep(1)
            elevador.piso_actual += elevador.direccion
            print(f"\033[94m[ELEVADOR] Movimiento al piso {elevador.piso_actual}, Dirección: {'ARRIBA' if elevador.direccion == 1 else 'ABAJO'}\033[0m\n")
            time.sleep(1)
            
            # Notificar movimiento
            elevador.condicion_movimiento.notify_all()
            elevador.condicion_subida.notify_all()

def logicaPersona(id_persona, elevador):
    piso_actual = random.randint(0, elevador.PISOS-1)
    piso_destino = random.randint(0, elevador.PISOS-1)
    
    while piso_destino == piso_actual:
        piso_destino = random.randint(0, elevador.PISOS-1)
    
    print(f"[SOLICITUD] Persona {id_persona} desea ir al piso {piso_destino} desde el piso {piso_actual}\n")
    time.sleep(1)  # Agregado para no mostrar tan rápido los mensajes iniciales
    
    # Registrar solicitud en el piso actual
    with elevador.lock_elevador:
        elevador.solicitudes[piso_actual].append(id_persona)
        print(f"[REGISTRO] Persona {id_persona} registrada en piso {piso_actual}\n")
    time.sleep(1)  # Agregado para espaciar los mensajes
    
    while piso_actual != piso_destino and elevador.funcionando:
        with elevador.lock_elevador:
            # Esperar elevador en piso actual con puertas abiertas
            while (elevador.piso_actual != piso_actual or not elevador.puerta_abierta):
                if not elevador.funcionando:
                    return
                elevador.condicion_subida.wait()
            
            # Intentar abordar si aún está en la lista de espera
            if id_persona in elevador.solicitudes[piso_actual]:
                if elevador.semaforo_capacidad.acquire(blocking=False):
                    # Abordar el elevador
                    elevador.solicitudes[piso_actual].remove(id_persona)
                    elevador.pasajeros.append((id_persona, piso_destino))
                    print(f"\033[92m[ENTRADA] Persona {id_persona} ha subido al elevador en el piso {piso_actual}. Destino: {piso_destino}\033[0m\n")  # Color verde
                    time.sleep(1)  # Agregado para espaciar los mensajes
                    
                    # Esperar dentro del elevador
                    while True:
                        if elevador.piso_actual == piso_destino and elevador.puerta_abierta:
                            # Salir del elevador
                            if (id_persona, piso_destino) in elevador.pasajeros:
                                elevador.pasajeros.remove((id_persona, piso_destino))
                                elevador.semaforo_capacidad.release()
                                piso_actual = piso_destino
                                print(f"\033[91m[LLEGADA] Persona {id_persona} ha llegado a su destino en el piso {piso_destino}\033[0m\n")  # Color rojo
                                time.sleep(1)  # Agregado para espaciar los mensajes
                            break
                        elevador.condicion_movimiento.wait()
                else:
                    print(f"\033[93m[AVISO] Persona {id_persona}. Elevador lleno, por favor espere...\033[0m\n")  # Color amarillo
                    time.sleep(1)  # Agregado para espaciar los mensajes
                    elevador.condicion_subida.wait()
            else:
                # Si ya no está en la lista de espera, significa que ya abordó
                elevador.condicion_subida.wait()

if __name__ == "__main__":
    # Mostrar animación inicial
    simularAscensor(9, 1)
    os.system("clear")  # Limpiar la pantalla después de la animación

    PISOS = 5
    personas = 10  # Aumentado para mejor demostración
    tiempo_simulacion = 60  # Aumentado para mejor demostración
    
    print("\n[INICIO] Hilevador 1.0\n")
    
    elevador = Elevador(PISOS)
    hilo_elevador = Thread(target=logicaElevador, args=(elevador,))
    hilo_elevador.start()
    
    hilos_personas = []
    for i in range(personas):
        t = Thread(target=logicaPersona, args=(i, elevador))
        t.start()
        hilos_personas.append(t)
        time.sleep(random.uniform(0.1, 0.3))  # Mayor dispersión en la llegada de personas
        
    time.sleep(tiempo_simulacion)
    
    elevador.detener()
    
    hilo_elevador.join()
    
    for hilo in hilos_personas:
        hilo.join()
    print("\n[FIN] Hilevador 1.0\n")
