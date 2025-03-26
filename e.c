#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>

#define PISOS 5  

#define RESET   "\033[0m"
#define AZUL    "\033[1;34m"
#define AMARILLO  "\033[1;33m"
#define VERDE   "\033[1;32m"

void dibujarAscensor(int pisoActual) {
    system("clear");

    for (int i = PISOS; i > 0; i--) {
        if (i == pisoActual) {
            printf(AZUL " [ ]  |  Piso %d \n" RESET, i); 
        } else {
            printf("      |  Piso %d\n", i);
        }
    }
}

void simularAscensor(int inicio, int fin) {
    int paso = (inicio < fin) ? 1 : -1;  

    for (int piso = inicio; piso != fin + paso; piso += paso) {
        dibujarAscensor(piso);

        if (paso == 1) {
            printf(AMARILLO "\nEl elevador esta subiendo...\n" RESET);
        } else {
            printf(AMARILLO "\nEl elevador esta bajando...\n" RESET);
        }
        
        usleep(800000);  
    }
    printf(VERDE "\nEl elevador ha llegado al piso %d :D!\n\n" RESET, fin);
}

int main() {
    srand(time(NULL));

    int piso_inicio, piso_fin;

    piso_inicio = (rand() % PISOS) + 1;
    
    do {
        piso_fin = (rand() % PISOS) + 1;
    } while (piso_fin == piso_inicio);

    simularAscensor(piso_inicio, piso_fin);

    return 0;
}
