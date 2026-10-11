#include "isam_core.h"
// Integracion nueva
#include "utils/builtins.h"
#include "lib/stringinfo.h"

extern IndexEntry *indice_estatico;
extern int total_entradas_indice;
//
PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(isam_build);

Datum
isam_build(PG_FUNCTION_ARGS)
{
    int paginas;

    paginas = construir_indice();

    PG_RETURN_INT32(paginas);
}

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
                    cstring_to_text(
                        actual->records[i].data
                    )
                );
            }
        }

        actual = actual->overflow;
    }

    PG_RETURN_NULL();
}
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

        while (pagina != NULL)
        {
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
        "Estadisticas ISAM\n"
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
 */
PG_FUNCTION_INFO_V1(isam_validate);

Datum
isam_validate(PG_FUNCTION_ARGS)
{
    StringInfoData salida;
    int errores = 0;
    int total_paginas = 0;
    int total_registros = 0;

    initStringInfo(&salida);

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

    for (int i = 0; i < total_entradas_indice; i++)
    {
        DataPage *principal = indice_estatico[i].page_ptr;

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
         * Detectar ciclos en la cadena de overflow.
         */
        DataPage *lento = principal;
        DataPage *rapido = principal;

        do
        {
            lento = lento ? lento->overflow : NULL;

            if (rapido != NULL)
            {
                rapido = rapido->overflow;
            }

            if (rapido != NULL)
            {
                rapido = rapido->overflow;
            }

            if (lento != NULL && lento == rapido)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: ciclo en overflow de pagina %d.\n",
                    i + 1
                );

                errores++;
                break;
            }
        }
        while (lento != NULL && rapido != NULL);

        /*
         * Validar el contenido de cada pagina.
         * No recorrer una cadena si se detecto un ciclo.
         */
        if (lento != NULL && lento == rapido)
        {
            continue;
        }

        DataPage *pagina = principal;

        while (pagina != NULL)
        {
            total_paginas++;

            if (pagina->current_count < 0 ||
                pagina->current_count > MAX_RECORDS)
            {
                appendStringInfo(
                    &salida,
                    "ERROR: cantidad invalida de registros "
                    "en pagina principal %d.\n",
                    i + 1
                );

                errores++;
                break;
            }

            total_registros += pagina->current_count;

            for (int j = 1; j < pagina->current_count; j++)
            {
                if (pagina->records[j - 1].search_key >
                    pagina->records[j].search_key)
                {
                    appendStringInfo(
                        &salida,
                        "ERROR: claves desordenadas "
                        "en pagina principal %d.\n",
                        i + 1
                    );

                    errores++;
                    break;
                }
            }

            pagina = pagina->overflow;
        }
    }

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
