// busqueda.c
#include "isam_core.h"
#include <stddef.h> 

// Este se conectará al array global

extern IndexEntry* indice_estatico;
extern int total_entradas_indice;

DataPage* buscar_pagina(int clave) {
    if (total_entradas_indice == 0 || indice_estatico == NULL) {
        return NULL; 
    }

    int izquierda = 0;
    int derecha = total_entradas_indice - 1;
    DataPage* pagina_destino = NULL; 

    while (izquierda <= derecha) {
        int medio = izquierda + (derecha - izquierda) / 2;

        if (indice_estatico[medio].first_key == clave) {
            return indice_estatico[medio].page_ptr;
            
        } else if (indice_estatico[medio].first_key < clave) {
            // Se guarda como candidata de límite inferior para búsqueda por rango
            pagina_destino = indice_estatico[medio].page_ptr;
            izquierda = medio + 1; 
            
        } else {
            derecha = medio - 1;
        }
    }

    // Si la clave es menor que la primera clave del índice,
    // debe dirigirse a la primera página.
    if (pagina_destino == NULL && clave < indice_estatico[0].first_key) {
        return indice_estatico[0].page_ptr;
    }
    
    return pagina_destino;
}
