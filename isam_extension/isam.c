#include "isam_core.h"

#include "utils/builtins.h"

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
