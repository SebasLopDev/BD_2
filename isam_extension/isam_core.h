// isam_core.h
#ifndef ISAM_CORE_H
#define ISAM_CORE_H

#include <postgres.h> // Obligatorio: nos da acceso a palloc y manejo de memoria
#include <fmgr.h>     // Obligatorio para crear funciones nativas (C-UDFs)

#define PAGE_SIZE 4096 
#define MAX_RECORDS 50 // Nuestro fill-factor para controlar el overflow

// Estructura de la tupla (Registro)
typedef struct {
    int search_key;       
    char data[60];        
} Record;

// Estructura de la Página de Datos (Nivel inferior y Overflow)
typedef struct DataPage {
    Record records[MAX_RECORDS]; 
    int current_count;           
    struct DataPage* overflow;   // Puntero a la siguiente página si esta se llena
} DataPage;

// Promesas de funciones (Lo que cada uno va a programar)
// María Belén:
DataPage* buscar_pagina(int clave);

// Sebastian:
void insertar_registro(Record nuevo_registro);

#endif