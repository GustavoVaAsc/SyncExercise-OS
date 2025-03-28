#include <stdio.h>
#include <stdlib.h>
#include <time.h>   
#include <omp.h>
#include <stdbool.h>

#ifdef _WIN32
    #include <Windows.h>
#else
    #include <unistd.h>
#endif

const int PERSONAS = 8;
const int ELEVADOR = 1;
#define PISOS 5
const int CAPACIDAD = 5;

// Definiciones de Multiplex y Torniquete

// Multiplex
typedef struct{
    int conteo;
    omp_lock_t lock;
} Multiplex;

// Torniquete
typedef struct{
    int esperando;
    bool liberado;
    omp_lock_t lock;
} Torniquete;

// Variables compartidas
int piso_actual = 0;
Multiplex capacidad;
Torniquete torniquete;
int solicitudes[PISOS];

// "Constructor" de las estructuras
void EstructurasSincronizacion(){
    capacidad.conteo = 0;
    omp_init_lock(&capacidad.lock);

    torniquete.esperando = 0;
    torniquete.liberado = false;
    omp_init_lock(&torniquete.lock);

    for(int i=0; i<PISOS; i++){
        solicitudes[i] = 0;
    }
}

// Entrar al Multiplex
void entrarMultiplex(Multiplex *m){
    while(true){
        omp_set_lock(&m->lock);
        if(m->conteo < CAPACIDAD){
            m->conteo++;
            omp_unset_lock(&m->lock);
            break;
        }
        omp_unset_lock(&m->lock);
        usleep(1000);
    }
}

// Salir del Multiplex
void salirMultiplex(Multiplex *m){
    omp_set_lock(&m->lock);
    if(m->conteo > 0) {
        m->conteo--;
    }
    omp_unset_lock(&m->lock);
}

void esperarTorniquete(Torniquete *t){
    omp_set_lock(&t->lock);
    t->esperando++;
    while(!t->liberado){
        omp_unset_lock(&t->lock);
        usleep(1000);
        omp_set_lock(&t->lock);
    }
    t->esperando--;
    if(t->esperando == 0){
        t->liberado = false;
    }

    omp_unset_lock(&t->lock);
}

void liberarTorniquete(Torniquete *t){
    omp_set_lock(&t->lock);
    t->liberado = true;
    omp_unset_lock(&t->lock);
}

void logicaElevador() {
    int direccion = 1;
    
    while(true) {
        // Procesar solicitudes
        printf("Piso: %d -- Pasajeros: %d \n",piso_actual,capacidad.conteo);
        if(solicitudes[piso_actual] < 0) {
            int bajando = -solicitudes[piso_actual];
            omp_set_lock(&capacidad.lock);
            bajando = (bajando > capacidad.conteo) ? capacidad.conteo : bajando;
            capacidad.conteo -= bajando;
            omp_unset_lock(&capacidad.lock);
            
            solicitudes[piso_actual] = 0;
            printf("[BAJAN] %d pasajeros en piso %d\n", bajando, piso_actual);
        }

        // Permitir nuevas subidas
        liberarTorniquete(&torniquete);
        usleep(500000);  // Tiempo en piso reducido a 0.5 segundos

        // Actualizar posición
        int nuevo_piso = piso_actual + direccion;
        if(nuevo_piso < 0 || nuevo_piso >= PISOS) {
            direccion *= -1;
            nuevo_piso = piso_actual + direccion;
        }
        
        #pragma omp atomic write
        piso_actual = nuevo_piso;
    }
}

void logicaPasajero(int id) {
    int piso_origen = rand() % PISOS;
    int piso_destino;
    do {
        piso_destino = rand() % PISOS;
    } while(piso_origen == piso_destino);

    printf("[NUEVO] Pasajero %d: %d → %d\n", id, piso_origen, piso_destino);

    // Registrar solicitud de subida
    #pragma omp atomic
    solicitudes[piso_origen]++;

    // Espera para subir
    int ha_subido = 0;
    while(!ha_subido) {
        int current_floor;
        #pragma omp atomic read
        current_floor = piso_actual;
        
        if(current_floor == piso_origen) {
            int puede_subir = 0;
            #pragma omp critical (subida)
            {
                if(solicitudes[piso_origen] > 0 && capacidad.conteo < CAPACIDAD) {
                    esperarTorniquete(&torniquete);
                    entrarMultiplex(&capacidad);
                    printf("[SUBIDA] Pasajero %d (%d → %d)\n", id, piso_origen, piso_destino);
                    solicitudes[piso_origen]--;
                    puede_subir = 1;
                }
            }
            if(puede_subir) {
                ha_subido = 1;
            }
        }
        usleep(50000);
    }

    // Registrar solicitud de bajada
    #pragma omp atomic
    solicitudes[piso_destino]--;

    // Espera para bajar
    int ha_bajado = 0;
    while(!ha_bajado) {
        int current_floor;
        #pragma omp atomic read
        current_floor = piso_actual;
        
        if(current_floor == piso_destino) {
            #pragma omp critical (bajada)
            {
                salirMultiplex(&capacidad);
                printf("[BAJADA] Pasajero %d en piso %d\n", id, piso_destino);
            }
            ha_bajado = 1;
        }
        usleep(50000);
    }
}

int main() {
    for(int i = 0; i < PISOS; i++) {
        solicitudes[i] = 0;
    }
    EstructurasSincronizacion();
    srand(time(NULL));

    // Configuración de hilos
    omp_set_nested(1);
    omp_set_num_threads(PERSONAS + 1);  // Pasajeros + elevador

    #pragma omp parallel
    {
        #pragma omp single nowait
        {
            // Hilo del elevador
            #pragma omp task
            logicaElevador();

            // Generar pasajeros
            #pragma omp taskloop num_tasks(PERSONAS)
            for(int i = 0; i < 20; i++) {
                logicaPasajero(i);
                usleep(rand() % 300000 + 100000); // Espera aleatoria 0.1-0.4s
            }
        }
    }
    return 0;
}