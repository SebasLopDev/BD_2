
#include "isam_core.h"

// Funciones auxiliares de PostgreSQL
#include "utils/builtins.h"
#include "lib/stringinfo.h"

// Variables globales del indice ISAM
extern IndexEntry *indice_estatico;
extern int total_entradas_indice;

PG_MODULE_MAGIC;


/*
 * Funcion auxiliar:
 * Detecta si una cadena de paginas overflow tiene ciclos.
 *
 * Utiliza el algoritmo de Floyd:
 * - lento avanza una pagina.
 * - rapido avanza dos paginas.
 * - Si ambos se encuentran, existe un ciclo.
 */
static int
tiene_ciclo_overflow(DataPage *principal)
{
    DataPage *lento = principal;
    DataPage *rapido = principal;

    while (rapido != NULL && rapido->overflow != NULL)
    {
        lento = lento->overflow;
        rapido = rapido->overflow->overflow;

        if (lento == rapido)
        {
            return 1;
        }
    }

    return 0;
}


/*
 * Construye el indice ISAM.
 */
PG_FUNCTION_INFO_V1(isam_build);

Datum
isam_build(PG_FUNCTION_ARGS)
{
    int paginas;

    paginas = construir_indice();

    PG_RETURN_INT32(paginas);
}


/*
 * Busca un registro por su clave.
 *
 * Primero obtiene la pagina principal correspondiente
 * y despues revisa sus paginas overflow.
 */
PG_FUNCTION_INFO_V1(isam_search);

Datum
isam_search(PG_FUNCTION_ARGS)
{
    int clave = PG_GETARG_INT32(0);

    DataPage *pagina;
    DataPage *actual;

    pagina = buscar_pagina(clave);

    if (pagina == NULL)
    {
        PG_RETURN_NULL();
    }

    actual = pagina;

    while (actual != NULL)
    {
        for (int i = 0; i < actual->current_count; i++)
        {
            if (actual->records[i].search_key == clave)
            {
                PG_RETURN_TEXT_P(
                    cstring_to_text(actual->records[i].data)
                );
            }
        }

        actual = actual->overflow;
    }

    PG_RETURN_NULL();
}


/*
 * Inserta un nuevo registro en el indice ISAM.
 */
PG_FUNCTION_INFO_V1(isam_insert);

Datum
isam_insert(PG_FUNCTION_ARGS)
{
    Record nuevo_registro;

    int clave = PG_GETARG_INT32(0);

    char *nombre = text_to_cstring(PG_GETARG_TEXT_PP(1));

    nuevo_registro.search_key = clave;

    strlcpy(
        nuevo_registro.data,
        nombre,
        sizeof(nuevo_registro.data)
    );

    pfree(nombre);

    insertar_registro_persistente(nuevo_registro);

    PG_RETURN_VOID();
}


/*
 * Muestra estadisticas generales del indice ISAM.
 */
PG_FUNCTION_INFO_V1(isam_stats);

Datum
isam_stats(PG_FUNCTION_ARGS)
{
    StringInfoData salida;

    int paginas_principales = total_entradas_indice;
    int paginas_overflow = 0;
    int total_registros = 0;

    initStringInfo(&salida);

    if (indice_estatico == NULL || total_entradas_indice == 0)
    {
        appendStringInfoString(
            &salida,
            "El indice ISAM no esta construido."
        );

        text *resultado = cstring_to_text(salida.data);
        pfree(salida.data);

        PG_RETURN_TEXT_P(resultado);
    }

    for (int i = 0; i < total_entradas_indice; i++)
    {
        DataPage *pagina = indice_estatico[i].page_ptr;

        if (pagina == NULL)
        {
            appendStringInfo(
                &salida,
                "ERROR: la pagina principal %d es NULL.\n",
                i + 1
            );

            continue;
        }

        if (tiene_ciclo_overflow(pagina))
        {
            appendStringInfo(
                &salida,
                "ERROR: ciclo detectado en overflow de pagina %d.\n",
                i + 1
            );

            continue;
        }

        while (pagina != NULL)
        {
            if (pagina->current_count < 0 ||
                pagina->current_count > MAX_RECORDS)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: cantidad invalida de registros "
                    "en pagina principal %d.\n",
                    i + 1
                );

                break;
            }

            total_registros += pagina->current_count;

            if (pagina != indice_estatico[i].page_ptr)
            {
                paginas_overflow++;
            }

            pagina = pagina->overflow;
        }
    }

    appendStringInfo(
        &salida,
        "\nEstadisticas ISAM\n"
        "Paginas principales: %d\n"
        "Paginas overflow: %d\n"
        "Total de paginas: %d\n"
        "Total de registros: %d",
        paginas_principales,
        paginas_overflow,
        paginas_principales + paginas_overflow,
        total_registros
    );

    text *resultado = cstring_to_text(salida.data);
    pfree(salida.data);

    PG_RETURN_TEXT_P(resultado);
}


/*
 * Muestra los registros almacenados en cada pagina.
 */
PG_FUNCTION_INFO_V1(isam_show_pages);

Datum
isam_show_pages(PG_FUNCTION_ARGS)
{
    StringInfoData salida;

    initStringInfo(&salida);

    if (indice_estatico == NULL || total_entradas_indice == 0)
    {
        appendStringInfoString(
            &salida,
            "El indice ISAM no esta construido."
        );

        text *resultado = cstring_to_text(salida.data);
        pfree(salida.data);

        PG_RETURN_TEXT_P(resultado);
    }

    int numero_pagina = 0;

    for (int i = 0; i < total_entradas_indice; i++)
    {
        DataPage *pagina = indice_estatico[i].page_ptr;
        int nivel_overflow = 0;

        if (pagina == NULL)
        {
            appendStringInfo(
                &salida,
                "\nERROR: la pagina principal %d es NULL.\n",
                i + 1
            );

            continue;
        }

        if (tiene_ciclo_overflow(pagina))
        {
            appendStringInfo(
                &salida,
                "\nERROR: ciclo detectado en overflow "
                "de la pagina principal %d.\n",
                i + 1
            );

            continue;
        }

        while (pagina != NULL)
        {
            numero_pagina++;

            appendStringInfo(
                &salida,
                "\nPagina %d | Principal %d | Overflow %d"
                " | Registros: %d\n",
                numero_pagina,
                i + 1,
                nivel_overflow,
                pagina->current_count
            );

            if (pagina->current_count < 0 ||
                pagina->current_count > MAX_RECORDS)
            {
                appendStringInfoString(
                    &salida,
                    "ERROR: cantidad invalida de registros.\n"
                );

                break;
            }

            for (int j = 0; j < pagina->current_count; j++)
            {
                appendStringInfo(
                    &salida,
                    "  Clave: %d | Dato: %s\n",
                    pagina->records[j].search_key,
                    pagina->records[j].data
                );
            }

            pagina = pagina->overflow;
            nivel_overflow++;
        }
    }

    text *resultado = cstring_to_text(salida.data);
    pfree(salida.data);

    PG_RETURN_TEXT_P(resultado);
}


/*
 * Comprueba la integridad basica de las paginas ISAM.
 *
 * Comprueba:
 * 1. Que el indice este construido.
 * 2. Que las paginas principales no sean NULL.
 * 3. Que no existan ciclos en las cadenas overflow.
 * 4. Que la cantidad de registros sea valida.
 * 5. Que las claves esten ordenadas dentro de cada pagina.
 * 6. Que las claves esten ordenadas entre paginas.
 * 7. Que first_key coincida con la primera clave
 *    de cada pagina principal.
 * 8. Que las entradas principales del indice esten ordenadas.
 */
PG_FUNCTION_INFO_V1(isam_validate);

Datum
isam_validate(PG_FUNCTION_ARGS)
{
    StringInfoData salida;

    int errores = 0;
    int total_paginas = 0;
    int total_registros = 0;

    int hay_clave_anterior = 0;
    int ultima_clave = 0;

    int hay_first_key_anterior = 0;
    int ultimo_first_key = 0;

    initStringInfo(&salida);

    /*
     * Comprobar si el indice existe.
     */
    if (indice_estatico == NULL || total_entradas_indice == 0)
    {
        appendStringInfoString(
            &salida,
            "ERROR: el indice ISAM no esta construido."
        );

        text *resultado = cstring_to_text(salida.data);
        pfree(salida.data);

        PG_RETURN_TEXT_P(resultado);
    }

    /*
     * Recorrer las paginas principales.
     */
    for (int i = 0; i < total_entradas_indice; i++)
    {
        DataPage *principal = indice_estatico[i].page_ptr;

        /*
         * Comprobar que la pagina principal exista.
         */
        if (principal == NULL)
        {
            appendStringInfo(
                &salida,
                "ERROR: la pagina principal %d es NULL.\n",
                i + 1
            );

            errores++;
            continue;
        }

        /*
         * Detectar ciclos en la cadena overflow.
         */
        if (tiene_ciclo_overflow(principal))
        {
            appendStringInfo(
                &salida,
                "ERROR: ciclo en overflow de pagina principal %d.\n",
                i + 1
            );

            errores++;

            /*
             * No recorremos esta cadena porque podria
             * provocar un bucle infinito.
             */
            continue;
        }

        /*
         * Validar la cantidad de registros de la pagina principal
         * antes de acceder a sus registros.
         */
        if (principal->current_count < 0 ||
            principal->current_count > MAX_RECORDS)
        {
            appendStringInfo(
                &salida,
                "ERROR: cantidad invalida de registros "
                "en pagina principal %d.\n",
                i + 1
            );

            errores++;
            continue;
        }

        /*
         * Comprobar que first_key coincida con la primera
         * clave de la pagina principal.
         */
        if (principal->current_count > 0)
        {
            if (indice_estatico[i].first_key !=
                principal->records[0].search_key)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: first_key no coincide con la "
                    "primera clave de la pagina principal %d.\n",
                    i + 1
                );

                errores++;
            }
        }

        /*
         * Comprobar que las entradas del indice principal
         * esten ordenadas.
         */
        if (principal->current_count > 0)
        {
            if (hay_first_key_anterior &&
                ultimo_first_key > indice_estatico[i].first_key)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: entradas principales del indice "
                    "desordenadas en la posicion %d.\n",
                    i + 1
                );

                errores++;
            }

            ultimo_first_key = indice_estatico[i].first_key;
            hay_first_key_anterior = 1;
        }

        /*
         * Recorrer la pagina principal y sus paginas overflow.
         */
        DataPage *pagina = principal;

        while (pagina != NULL)
        {
            total_paginas++;

            /*
             * Validar la cantidad de registros de cada pagina.
             */
            if (pagina->current_count < 0 ||
                pagina->current_count > MAX_RECORDS)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: cantidad invalida de registros "
                    "en la cadena de la pagina principal %d.\n",
                    i + 1
                );

                errores++;

                /*
                 * No acceder a records si el contador
                 * esta fuera de los limites permitidos.
                 */
                break;
            }

            total_registros += pagina->current_count;

            /*
             * Comprobar el orden entre paginas.
             *
             * ultima_clave contiene la ultima clave de la
             * pagina anterior.
             *
             * La primera clave de la pagina actual no debe
             * ser menor que esa clave anterior.
             */
            if (pagina->current_count > 0)
            {
                if (hay_clave_anterior &&
                    ultima_clave > pagina->records[0].search_key)
                {
                    appendStringInfo(
                        &salida,
                        "ERROR: claves desordenadas entre paginas "
                        "en el indice principal %d.\n",
                        i + 1
                    );

                    errores++;
                }

                /*
                 * Comprobar el orden dentro de la pagina.
                 */
                for (int j = 1; j < pagina->current_count; j++)
                {
                    if (pagina->records[j - 1].search_key >
                        pagina->records[j].search_key)
                    {
                        appendStringInfo(
                            &salida,
                            "ERROR: claves desordenadas dentro "
                            "de una pagina del indice principal %d.\n",
                            i + 1
                        );

                        errores++;
                        break;
                    }
                }

                /*
                 * Guardar la ultima clave para compararla
                 * con la siguiente pagina.
                 */
                ultima_clave =
                    pagina->records[pagina->current_count - 1].search_key;

                hay_clave_anterior = 1;
            }

            pagina = pagina->overflow;
        }
    }

    /*
     * Mostrar el resultado de la validacion.
     */
    if (errores == 0)
    {
        appendStringInfoString(
            &salida,
            "VALIDACION CORRECTA: no se detectaron "
            "errores en las comprobaciones realizadas.\n"
        );
    }
    else
    {
        appendStringInfo(
            &salida,
            "VALIDACION FALLIDA: %d error(es).\n",
            errores
        );
    }

    appendStringInfo(
        &salida,
        "Paginas recorridas: %d\n"
        "Registros contabilizados: %d",
        total_paginas,
        total_registros
    );

    text *resultado = cstring_to_text(salida.data);
    pfree(salida.data);

    PG_RETURN_TEXT_P(resultado);
}
