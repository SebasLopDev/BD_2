// construccion.c

#include "isam_core.h"

#include "executor/spi.h"
#include "utils/builtins.h"
#include "utils/memutils.h"

IndexEntry *indice_estatico = NULL;
int total_entradas_indice = 0;

/* Contexto para conservar el indice entre llamadas SQL. */
static MemoryContext contexto_isam = NULL;

int construir_indice(void)
{
    int ret;
    uint64 cantidad;

    ret = SPI_connect();

    if (ret != SPI_OK_CONNECT)
    {
        elog(ERROR, "No se pudo conectar mediante SPI");
    }

    ret = SPI_execute(
        "SELECT id_paciente, nombre "
        "FROM paciente "
        "ORDER BY id_paciente",
        true,
        0
    );

    if (ret != SPI_OK_SELECT)
    {
        SPI_finish();
        elog(ERROR, "No se pudo consultar la tabla paciente");
    }

    cantidad = SPI_processed;

    /*
     * Eliminar el indice anterior despues de comprobar
     * que la consulta se ejecuto correctamente.
     */
    if (contexto_isam != NULL)
    {
        MemoryContextDelete(contexto_isam);
        contexto_isam = NULL;
    }

    indice_estatico = NULL;
    total_entradas_indice = 0;

    if (cantidad == 0)
    {
        SPI_finish();
        return 0;
    }

    /*
     * Crear un contexto que sobreviva al final de esta
     * llamada SQL dentro del backend actual.
     */
    contexto_isam = AllocSetContextCreate(
        TopMemoryContext,
        "ISAM index context",
        ALLOCSET_DEFAULT_SIZES
    );

    MemoryContext contexto_anterior =
        MemoryContextSwitchTo(contexto_isam);

    total_entradas_indice =
        (cantidad + MAX_RECORDS - 1) / MAX_RECORDS;

    indice_estatico =
        palloc0(sizeof(IndexEntry) * total_entradas_indice);

    for (int i = 0; i < total_entradas_indice; i++)
    {
        indice_estatico[i].page_ptr =
            palloc0(sizeof(DataPage));

        indice_estatico[i].page_ptr->current_count = 0;
        indice_estatico[i].page_ptr->overflow = NULL;
    }

    for (uint64 i = 0; i < cantidad; i++)
    {
        bool is_null_id;
        bool is_null_nombre;

        Datum id_datum = SPI_getbinval(
            SPI_tuptable->vals[i],
            SPI_tuptable->tupdesc,
            1,
            &is_null_id
        );

        Datum nombre_datum = SPI_getbinval(
            SPI_tuptable->vals[i],
            SPI_tuptable->tupdesc,
            2,
            &is_null_nombre
        );

        if (is_null_id)
        {
            continue;
        }

        int id = DatumGetInt32(id_datum);

        char *nombre;

        if (is_null_nombre)
        {
            nombre = "";
        }
        else
        {
            nombre = TextDatumGetCString(nombre_datum);
        }

        int pagina_index = i / MAX_RECORDS;

        int posicion =
            indice_estatico[pagina_index]
                .page_ptr
                ->current_count;

        indice_estatico[pagina_index]
            .page_ptr
            ->records[posicion]
            .search_key = id;

        strlcpy(
            indice_estatico[pagina_index]
                .page_ptr
                ->records[posicion]
                .data,
            nombre,
            sizeof(
                indice_estatico[pagina_index]
                    .page_ptr
                    ->records[posicion]
                    .data
            )
        );

        indice_estatico[pagina_index]
            .page_ptr
            ->current_count++;

        indice_estatico[pagina_index].first_key =
            indice_estatico[pagina_index]
                .page_ptr
                ->records[0]
                .search_key;
    }

    /*
     * Restaurar el contexto anterior antes de finalizar SPI.
     */
    MemoryContextSwitchTo(contexto_anterior);

    SPI_finish();

    return total_entradas_indice;
}
void insertar_registro_persistente(Record nuevo_registro)
{
    if (contexto_isam == NULL)
    {
        elog(ERROR, "Primero debe ejecutar isam_build()");
    }

    MemoryContext contexto_anterior =
        MemoryContextSwitchTo(contexto_isam);

    insertar_registro(nuevo_registro);

    MemoryContextSwitchTo(contexto_anterior);
}
