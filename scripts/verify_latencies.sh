#!/usr/bin/env bash
set -euo pipefail

export MSYS_NO_PATHCONV=1

TOLERANCE=3
failures=0

if ! docker_err=$(docker info 2>&1 >/dev/null); then
    echo "ERROR: No se pudo conectar con el daemon de Docker. Verifica que Docker este en ejecucion y tengas permisos." >&2
    if [ -n "$docker_err" ]; then
        echo "Detalle: ${docker_err}" >&2
    fi
    exit 1
fi

check_pair() {
    local label="$1"
    local src_node="$2"
    local dst_ip="$3"
    local expected="$4"
    local ping_output avg_rtt

    if ! ping_output=$(docker exec -u root "$src_node" env LC_ALL=C ping -c 4 "$dst_ip" 2>&1); then
        echo "[FAIL] ${label} (${src_node} -> ${dst_ip}): fallo al ejecutar ping"
        echo "       $(printf '%s\n' "$ping_output" | tail -n 2)"
        failures=$((failures + 1))
        return
    fi

    avg_rtt=$(printf '%s\n' "$ping_output" | LC_ALL=C awk -F'=' '/(rtt|round-trip)/ {
        split($2, a, "/")
        gsub(/^[ \t]+/, "", a[2])
        print a[2]
    }')

    if [ -z "$avg_rtt" ]; then
        echo "[FAIL] ${label} (${src_node} -> ${dst_ip}): no se pudo extraer el RTT promedio"
        failures=$((failures + 1))
        return
    fi

    if LC_ALL=C awk -v avg="$avg_rtt" -v target="$expected" -v tol="$TOLERANCE" 'BEGIN {
        diff = avg - target
        if (diff < 0) diff = -diff
        exit (diff <= tol ? 0 : 1)
    }'; then
        echo "[OK]   ${label} (${src_node} -> ${dst_ip}): RTT promedio = ${avg_rtt} ms (esperado: ${expected} ms +/- ${TOLERANCE} ms)"
    else
        echo "[FAIL] ${label} (${src_node} -> ${dst_ip}): RTT promedio = ${avg_rtt} ms (esperado: ${expected} ms +/- ${TOLERANCE} ms)"
        failures=$((failures + 1))
    fi
}

echo "Verificando latencias entre nodos (4 paquetes ICMP por par, tolerancia +/- ${TOLERANCE} ms)..."
check_pair "A -> B" "nodo_a" "172.25.0.20" "20"
check_pair "A -> C" "nodo_a" "172.25.0.30" "40"
check_pair "B -> C" "nodo_b" "172.25.0.30" "25"

if [ "$failures" -gt 0 ]; then
    echo "Verificacion fallida: ${failures} par(es) fuera de rango o inaccesibles." >&2
    exit 1
fi

echo "Verificacion exitosa: todos los pares cumplen la latencia esperada."
