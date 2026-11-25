#!/usr/bin/env bash

(
    set -e
    export LC_ALL=C

    for dir in /init-scripts/common /init-scripts/local; do
        [ -d "$dir" ] || continue
        for f in "$dir"/*; do
            [ -f "$f" ] || continue
            case "$f" in
                *.sql)
                    echo "[00-run-all] Ejecutando SQL: $f"
                    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f "$f"
                    ;;
                *.sh)
                    echo "[00-run-all] Ejecutando script: $f"
                    bash "$f"
                    ;;
                *)
                    echo "[00-run-all] Ignorando archivo: $f"
                    ;;
            esac
        done
    done
)
