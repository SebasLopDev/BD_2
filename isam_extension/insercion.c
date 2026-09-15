// insercion.c
#include "isam_core.h"

void insertar_registro(Record nuevo_registro) {
    // 1. Llamada a la función de búsqueda (con mock data)
    DataPage* pagina = buscar_pagina(nuevo_registro.search_key);
    
    if (pagina == NULL) {
        // Manejar error
        return;
    }
    
    // 2. Lógica de inserción y Overflow
    if (pagina->current_count < MAX_RECORDS) {
        // TODO (Sebastian): Insertar normal y reordenar la página
    } else {
        // TODO (Sebastian): ¡Página llena! 
        // Usar palloc() para crear una nueva DataPage en el área de overflow
        // y enlazarla con pagina->overflow
    }
}