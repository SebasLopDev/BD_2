
// insercion.c

#include "isam_core.h"

extern IndexEntry *indice_estatico;
extern int total_entradas_indice;

// Comprueba si una clave ya existe en la página principal
// o en alguna de sus páginas overflow.
static int existe_clave(DataPage *pagina, int clave) {

    while (pagina != NULL) {

        for (int i = 0; i < pagina->current_count; i++) {

            if (pagina->records[i].search_key == clave) {
                return 1;
            }
        }

        pagina = pagina->overflow;
    }

    return 0;
}

// Inserta un registro en una página que tiene espacio.
// Mantiene los registros ordenados por search_key.
static void insertar_en_pagina(DataPage *pagina, Record registro) {

    int i = pagina->current_count;

    while (i > 0 &&
           pagina->records[i - 1].search_key > registro.search_key) {

        pagina->records[i] = pagina->records[i - 1];
        i--;
    }

    pagina->records[i] = registro;
    pagina->current_count++;
}


// Actualiza first_key cuando cambia el primer registro
// de una página principal.
static void actualizar_first_key(DataPage *pagina) {

    for (int i = 0; i < total_entradas_indice; i++) {

        if (indice_estatico[i].page_ptr == pagina) {

            if (pagina->current_count > 0) {
                indice_estatico[i].first_key =
                    pagina->records[0].search_key;
            }

            return;
        }
    }
}


void insertar_registro(Record nuevo_registro) {

    // 1. Comprobar que el índice existe.
    if (indice_estatico == NULL || total_entradas_indice == 0) {
        ereport(ERROR,
                (errmsg("El indice ISAM no esta construido")));
    }

    // 2. Buscar la página principal correspondiente.
    DataPage *pagina_principal =
        buscar_pagina(nuevo_registro.search_key);

    if (pagina_principal == NULL) {
        ereport(ERROR,
                (errmsg("No se encontro una pagina para la clave")));
    }

    // 3. Buscar la página donde corresponde insertar.
    DataPage *destino = pagina_principal;

    while (destino->overflow != NULL &&
           destino->current_count > 0 &&
           nuevo_registro.search_key >
               destino->records[destino->current_count - 1].search_key) {

        destino = destino->overflow;
    }

    // 4. Comenzar la inserción.
    Record pendiente = nuevo_registro;
    DataPage *actual = destino;

    while (1) {

        // Caso A: la página tiene espacio.
        if (actual->current_count < MAX_RECORDS) {

            insertar_en_pagina(actual, pendiente);

            // Solo la página principal tiene entrada en el índice.
            if (actual == pagina_principal) {
                actualizar_first_key(actual);
            }

            return;
        }

        // Caso B: la página está llena.
        // Creamos un arreglo temporal de 51 registros.
        Record temporal[MAX_RECORDS + 1];

        int i = 0;
        int j = 0;
        int insertado = 0;

        // Insertar el nuevo registro en su posición ordenada.
        while (i < MAX_RECORDS) {

            if (!insertado &&
                pendiente.search_key <
                    actual->records[i].search_key) {

                temporal[j++] = pendiente;
                insertado = 1;
            }

            temporal[j++] = actual->records[i++];
        }

        // Si la clave es mayor o igual que todas las existentes,
        // se coloca al final.
        if (!insertado) {
            temporal[j] = pendiente;
        }

        // Los primeros 50 registros permanecen en esta página.
        for (int k = 0; k < MAX_RECORDS; k++) {
            actual->records[k] = temporal[k];
        }

        // El último registro debe pasar a la siguiente página.
        pendiente = temporal[MAX_RECORDS];

        // Si estamos modificando la página principal,
        // actualizar su primera clave.
        if (actual == pagina_principal) {
            actualizar_first_key(actual);
        }

        // 5. Avanzar a la página siguiente.
        if (actual->overflow == NULL) {

            DataPage *nueva_pagina = palloc0(sizeof(DataPage));

            nueva_pagina->current_count = 0;
            nueva_pagina->overflow = NULL;

            actual->overflow = nueva_pagina;
        }

        actual = actual->overflow;
    }
}
