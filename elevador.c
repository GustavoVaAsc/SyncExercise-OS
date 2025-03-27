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
    m->conteo--;
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

void logicaElevador(){
    int direccion = 1; // 1 -> Arriba, -1 -> Abajo
    
    while(true){
        printf("Piso: %d -- Pasajeros: %d \n",piso_actual,capacidad.conteo);
        

        if(solicitudes[piso_actual] < 0){
            int bajando = -solicitudes[piso_actual];
            if(bajando > capacidad.conteo) bajando  = capacidad.conteo;
            
            for(int i=0; i<bajando; i++){
                salirMultiplex(&capacidad);
            }

            solicitudes[piso_actual] = 0;
            printf("%d pasajeros bajaron en el piso %d \n",bajando,piso_actual);
        }

        // Liberar el torniquete
        liberarTorniquete(&torniquete);

        sleep(1);

        piso_actual+=direccion;
        if(piso_actual <= 0){
            piso_actual = 0;
            direccion = 1;
        }else if(piso_actual = PISOS-1){
            piso_actual = PISOS-1;
            direccion -1;
        }
    }
}

void logicaPasajero(int id){
    int piso_origen = rand()%PISOS;
    int piso_destino;
    do{
        piso_destino = rand()%PISOS;
    }while(piso_origen == piso_destino);

    printf("Solicitud: Pasajero: %d --- Piso de Origen: %d --- Piso destino:  %d \n", id,piso_origen,piso_destino);

    // Hacer solicitud para subir con atomic

    #pragma omp atomic
    solicitudes[piso_origen]++;

    while(piso_actual != piso_destino){
        usleep(1000);
    }

    salirMultiplex(&capacidad);
    printf("Pasajero: %d baja en el piso %d \n",id, piso_destino);
}

int main(){
    EstructurasSincronizacion();
    srand(time(NULL));

    #pragma omp parallel sections num_threads(2)
    {
        #pragma omp section
        {
            logicaElevador();
        }

        #pragma omp section
        {
            #pragma omp parallel for num_threads(PERSONAS)
            for(int i=0; i<20; i++){
                logicaPasajero(i);
                sleep(rand()%3 +1);
            }
        }
    }

    return 0;
}