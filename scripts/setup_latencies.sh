#!/usr/bin/env bash
set -euo pipefail

export MSYS_NO_PATHCONV=1

MAX_WAIT=120
NODES="nodo_a nodo_b nodo_c"
INSPECT_FMT='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}'

if ! docker_err=$(docker info 2>&1 >/dev/null); then
    echo "ERROR: No se pudo conectar con el daemon de Docker. Verifica que Docker este en ejecucion y tengas permisos." >&2
    if [ -n "$docker_err" ]; then
        echo "Detalle: ${docker_err}" >&2
    fi
    exit 1
fi

echo "Esperando a que los contenedores (${NODES}) alcancen estado healthy (maximo ${MAX_WAIT}s)..."
elapsed=0
all_healthy=0

while [ "$elapsed" -lt "$MAX_WAIT" ]; do
    all_healthy=1
    for node in $NODES; do
        status=$(docker inspect --format "$INSPECT_FMT" "$node" 2>/dev/null || echo "no_encontrado")
        if [ "$status" != "healthy" ]; then
            all_healthy=0
            break
        fi
    done

    if [ "$all_healthy" -eq 1 ]; then
        echo "Todos los nodos estan healthy (${elapsed}s)."
        break
    fi

    sleep 2
    elapsed=$((elapsed + 2))
done

if [ "$all_healthy" -ne 1 ]; then
    echo "ERROR: Tiempo de espera agotado (${MAX_WAIT}s). Los siguientes nodos no alcanzaron el estado healthy:" >&2
    for node in $NODES; do
        if status=$(docker inspect --format "$INSPECT_FMT" "$node" 2>&1); then
            if [ "$status" != "healthy" ]; then
                echo "  - ${node}: estado actual '${status}'" >&2
            fi
        else
            echo "  - ${node}: error al inspeccionar (${status})" >&2
        fi
    done
    exit 1
fi

apply_tc_rules() {
    local node="$1"
    local ip1="$2"
    local delay1="$3"
    local ip2="$4"
    local delay2="$5"

    echo "Aplicando reglas tc en ${node}: ${ip1} -> ${delay1} (banda 1:1), ${ip2} -> ${delay2} (banda 1:2)..."

    if ! docker exec -u root "$node" sh -c "
        set -e
        tc qdisc del dev eth0 root 2>/dev/null || true
        tc qdisc add dev eth0 root handle 1: prio bands 3 priomap 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2
        tc qdisc add dev eth0 parent 1:1 handle 10: netem delay ${delay1}
        tc qdisc add dev eth0 parent 1:2 handle 20: netem delay ${delay2}
        tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst ${ip1}/32 flowid 1:1
        tc filter add dev eth0 protocol ip parent 1:0 prio 2 u32 match ip dst ${ip2}/32 flowid 1:2
    "; then
        echo "ERROR: Fallo la configuracion de tc en '${node}'." >&2
        echo "El kernel del host o de Docker/WSL2 puede no incluir los modulos 'sch_netem' o 'sch_prio' (o el contenedor no tiene cap_add NET_ADMIN)." >&2
        exit 1
    fi
}

# Delays de salida configurados para lograr RTT objetivo:
#   A <-> B = 20 ms (10 ms + 10 ms)
#   A <-> C = 40 ms (20 ms + 20 ms)
#   B <-> C = 25 ms (12.5 ms + 12.5 ms)
apply_tc_rules "nodo_a" "172.25.0.20" "10ms"   "172.25.0.30" "20ms"
apply_tc_rules "nodo_b" "172.25.0.10" "10ms"   "172.25.0.30" "12.5ms"
apply_tc_rules "nodo_c" "172.25.0.10" "20ms"   "172.25.0.20" "12.5ms"

echo "Latencias configuradas correctamente en nodo_a, nodo_b y nodo_c."
