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
        self.capacidad = 5 # Capacidad del elevador
        self.piso_actual = 0 # Piso actual
        self.direccion = 1 # Direccion (1 - arriba, -1 - abajo)
        self.pasajeros = [] # Lista de pasajeros (Hilos)
        self.solicitudes = defaultdict(list) # Lista de solicitudes para acceder al elevador
        self.puerta_abierta = False # Booleano para saber si la puerta está abierta
        self.PISOS = PISOS # Inicializando la cantidad de pisos totales
        self.funcionando = True # Booleano para saber si el elevador está funcionando
        self.lock_elevador = Lock() # Lock para proteger el elevador
        self.condicion_subida = Condition(self.lock_elevador) # Coordinar la condicion para subir
        self.condicion_movimiento = Condition(self.lock_elevador) # Coordinar a los pasajeros para bajar donde deben
        self.semaforo_capacidad = BoundedSemaphore(self.capacidad)  # Controla que la capacidad maxima sea realmente 5
    
    # Metodo para detener
    def detener(self):
        with self.lock_elevador: 
            self.funcionando = False
            self.condicion_subida.notify_all()
            self.condicion_movimiento.notify_all()

# Función para controlar el elevador
def logicaElevador(elevador):
    while elevador.funcionando:
        with elevador.lock_elevador:
            if not elevador.funcionando:
                break
            
            # 0.- Verificar si hay solicitudes o pasajeros
            hay_solicitudes = any(len(personas) > 0 for personas in elevador.solicitudes.values())
            hay_pasajeros = len(elevador.pasajeros) > 0

            # Si no hay, entrar al modo reposo
            if not hay_solicitudes and not hay_pasajeros:
                # Modo reposo: mover al piso 0 y esperar
                if elevador.piso_actual != 0:
                    elevador.direccion = -1  # Bajar al piso 0
                    elevador.piso_actual = 0
                    print(f"\033[94m[ELEVADOR] No hay solicitudes. Moviendo al piso 0 (reposo)\033[0m\n")
                else:
                    print("\033[94m[ELEVADOR] En reposo (piso 0). Esperando solicitudes...\033[0m\n")
                    elevador.condicion_subida.wait(timeout=5.0)  # Timeout para evitar bloqueo
                continue  # Volver a verificar condiciones
            
            # 1. Dejar bajar pasajeros (prioridad)
            pasajeros_bajando = [p for p in elevador.pasajeros if p[1] == elevador.piso_actual]
            if pasajeros_bajando: # Si la lista no está vacía
                elevador.puerta_abierta = True # Abrir la puerta
                print(f"\033[94m[ELEVADOR] Piso {elevador.piso_actual}: Bajando pasajeros\033[0m")
                for pasajero in pasajeros_bajando: # Bajar cada pasajero
                    elevador.pasajeros.remove(pasajero) # Lo removemos de la lista de pasajeros
                    elevador.semaforo_capacidad.release() # Liberamos el semáforo por cada pasajero que baje.
                    print(f"\033[91m[BAJADA] Persona {pasajero[0]} bajó en el piso {elevador.piso_actual}\033[0m")  # Mostrar piso de bajada
                time.sleep(1)  # Tiempo para descenso

            # 2. Subir nuevos pasajeros (si hay espacio y solicitudes)
            if elevador.piso_actual in elevador.solicitudes and elevador.solicitudes[elevador.piso_actual]:
                elevador.puerta_abierta = True # Abrir puerta
                print(f"\033[94m[ELEVADOR] Piso {elevador.piso_actual}: Subiendo pasajeros\033[0m")
                elevador.condicion_subida.notify_all()  # Notificar a los que esperan
                elevador.condicion_subida.wait(timeout=2.0)  # Espera con timeout

            # 3. Cerrar puertas y continuar
            elevador.puerta_abierta = False
            print(f"\033[94m[ELEVADOR] Puertas cerradas. Pasajeros: {len(elevador.pasajeros)}\033[0m")
            
            # 4. Calcular próximo piso (SCAN dinámico)
            proximos_pisos = [] # Lista de próximos pisos
            
            # Agrega pisos con personas esperando
            for piso, personas in elevador.solicitudes.items(): 
                if personas:
                    proximos_pisos.append(piso)
                    
            # Agrega pisos destino de pasajeros actuales
            for (_, piso) in elevador.pasajeros:
                proximos_pisos.append(piso)

            # 5. Cambiar dirección si no hay más solicitudes en la dirección actual
            if not proximos_pisos:
                if elevador.piso_actual == elevador.PISOS - 1: # Si llegamos al limite superior, bajar
                    elevador.direccion = -1
                elif elevador.piso_actual == 0: # Si llegamos al limite inferior, subir
                    elevador.direccion = 1
            else:
                if elevador.direccion == 1:
                    if not any(p > elevador.piso_actual for p in proximos_pisos): # Cambiar a bajar con base en los próximos pisos de los pasajeros
                        elevador.direccion = -1
                else:
                    if not any(p < elevador.piso_actual for p in proximos_pisos): # Cambiar a subir con base en los próximos pisos de los pasajeros
                        elevador.direccion = 1

            # 6. Mover
            next_piso = elevador.piso_actual + elevador.direccion
            next_piso = max(0, min(elevador.PISOS - 1, next_piso))

        # Movimiento
        time.sleep(1)  # Simular tiempo de movimiento
        with elevador.lock_elevador:
            elevador.piso_actual = next_piso
            print(f"\033[94m[ELEVADOR] Movimiento → Piso {elevador.piso_actual} ({'↑' if elevador.direccion == 1 else '↓'})\033[0m")
            elevador.condicion_movimiento.notify_all()  # Notificar a pasajeros en movimiento

def logicaPersona(id_persona, elevador):
    piso_actual = random.randint(0, elevador.PISOS - 1) # Desde piso aleatorio
    piso_destino = random.randint(0, elevador.PISOS - 1) # Hasta piso aleatorio
    while piso_destino == piso_actual:
        piso_destino = random.randint(0, elevador.PISOS - 1)

    print(f"[SOLICITUD] Persona {id_persona} quiere ir de {piso_actual} → {piso_destino}")
    time.sleep(random.uniform(0.1, 0.5))

    # Registrar solicitud (puede hacerse en cualquier momento)
    with elevador.lock_elevador:
        elevador.solicitudes[piso_actual].append(id_persona)

    while piso_actual != piso_destino and elevador.funcionando:
        with elevador.lock_elevador:
            # Esperar a que el elevador llegue al piso y abra puertas
            while (elevador.piso_actual != piso_actual or not elevador.puerta_abierta) and elevador.funcionando:
                elevador.condicion_subida.wait(timeout=1.0)  # Timeout para evitar deadlock

            if not elevador.funcionando:
                return

            # Intenta subir al elevador si hay espacio
            if id_persona in elevador.solicitudes[piso_actual]:
                # Verifica si hay cupo disponible usando el semaforo
                if elevador.semaforo_capacidad.acquire(blocking=False):
                    # Registra al pasajero en el elevador
                    elevador.solicitudes[piso_actual].remove(id_persona)
                    elevador.pasajeros.append((id_persona, piso_destino))
                    print(f"\033[92m[ENTRADA] Persona {id_persona} subió en piso {elevador.piso_actual}\033[0m")
                    
                    # Espera hasta llegar al destino
                    while elevador.piso_actual != piso_destino and elevador.funcionando:
                        elevador.condicion_movimiento.wait(timeout=1.0)
                    
                    # Proceso de bajada
                    if elevador.piso_actual == piso_destino and elevador.puerta_abierta:
                        #elevador.pasajeros.remove((id_persona, piso_destino))
                        #elevador.semaforo_capacidad.release()
                        print(f"\033[91m[LLEGADA] Persona {id_persona} bajó en piso {elevador.piso_actual}\033[0m")
                        return
                else:
                    # Elevador lleno, espera
                    print(f"\033[93m[AVISO] Elevador lleno. Persona {id_persona} espera en piso {elevador.piso_actual}\033[0m")
                    elevador.condicion_subida.wait(timeout=1.0)       
                    
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