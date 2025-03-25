#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#ifdef _WIN32
    #include <Windows.h>
#else
    #include <unistd.h>
#endif

const int PERSONAS = 8;
const int ELEVADOR = 1;
const int PISOS = 5;

// Variables compartidas
int piso_actual = 0;
int pasajeros = 0;
int solicitudes[PISOS] = {0};
omp_lock_t lock_elevador;

void logicaElevador(){

}

void logicaPasajero(){
    
}

int main(){

    return 0;
}