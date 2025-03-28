# SyncExercise-OS

Entrega de la primera tarea de la materia Sistemas Operativos Semestre 2025-2 por Yordi Jiménez y Gustavo Valenzuela

## Problema

Decidimos optar por el problema "El elevador" el cual plantea lo siguiente:

- El elevador de la Facultad se descompone demasiado, porque
sus usuarios no respetan los límites. 

    * Te toca evitar este desgaste (y el peligro que conlleva).

- Implementa el elevador como un hilo, y a cada persona que
quiere usarlo como otro hilo.

- El elevador de la Facultad de Ingeniería da servicio a cinco
pisos.

    * Un usuario puede llamarlo en cualquiera de ellos
    * Puede querer ir a cualquiera otro de ellos.

- El elevador tiene capacidad para cinco pasajeros

    * Recuerden que el peso canónico de todo ingeniero (estudiante o docente) es constante.

- Para ir del piso x a y, el elevador tiene que cruzar todos los pisos intermedios

- Los usuarios prefieren esperar dentro del elevador que fuera de él

## Lenguaje y entorno

Nuestro trabajo esta realizado en su totalidad con el lenguaje Python, usando al biblioteca threading.

## Estrategia de sincronizacion

Usamos un semáforo acotado para poder controlar la cantidad de personas que subían al elevador, a su vez
ocupamos dos condiciones para poder controlar la subida y bajada de los pasajeros (debe suceder cuando estén en el
piso al que desean ir y cuando las puertas del elevador estén abiertas).

## ¿Cómo evitamos la inanición?

Usamos el algoritmo SCAN para prevenir que haya monopolio entre hilos, eventualmente atendiendo todas las solicitudes.

SCAN es un algoritmo de planificación de disco (usado también en sistemas de elevadores) que funciona de manera similar a un elevador:

- Barre en una dirección (generalmente de abajo hacia arriba primero).

- Atiende todas las solicitudes que encuentra en su camino.

- Cuando llega al extremo (piso más alto o más bajo), cambia de dirección y repite el proceso.


