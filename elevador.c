#include <stdio.h>
#include <stdlib.h>
#include <omp.h>
#include <stdbool.h>

#ifdef _WIN32
    #include <Windows.h>
#else
    #include <unistd.h>
#endif

const int PERSONAS = 8;
const int ELEVADOR = 1;
const int PISOS = 5;

// Definiciones de Multiplex y Torniquete
typedef struct{
    int count;
    omp_lock_t lock;
} Mulitplex;

// Variables compartidas
int piso_actual = 0;
int pasajeros = 0;
int solicitudes[PISOS] = {0};
omp_lock_t lock_elevador;

void logicaElevador(){

}

void logicaPasajero(int id){

}

int main(){
    omp_init_lock(&lock_elevador);

    #pragma omp parallel sections
    {
        #pragma omp section
        {
            logicaElevador();
        }

        #pragma omp section
        {
            #pragma omp parallel for
            for(int i=0; i<20; i++){
                logicaPasajero(i);
                sleep(rand()%3 +1);
            }
        }
    }
    omp_destroy_lock(&lock_elevador);
    return 0;
}