# Infraestructura Distribuida (3 Nodos PostgreSQL)

Esta guía describe cómo levantar, configurar y verificar el entorno distribuido de 3 nodos PostgreSQL (`nodo_a`, `nodo_b` y `nodo_c`) con red dedicada e inyección de latencias simuladas mediante `tc netem`.

---

## 1. Requisitos previos

- **Docker** y **Docker Compose v2** (`docker compose`).
- **Bash** (Linux, macOS o Git Bash / WSL en Windows).

> **Nota importante para Windows:**
> - Los scripts en `scripts/` deben ejecutarse desde **Git Bash** o **WSL** (**no** desde PowerShell ni CMD).
> - Docker Desktop debe estar configurado con el backend **WSL2**.

> **Convivencia con el entorno ISAM (`compose.yml`):**
> - El repositorio ya contiene un `compose.yml` para el módulo ISAM (`postgres_isam`), al cual Docker Compose da prioridad por defecto si no se pasa `-f`.
> - Por ello, **todos** los comandos de este entorno distribuido deben usar explícitamente `-f docker-compose.yml` (que además utiliza el proyecto separado `name: bd2_distribuido`).
> - **Conflicto de puerto:** `nodo_a` expone el puerto `5433` en el host, el mismo que `postgres_isam`. **No ejecutes ambos entornos a la vez** (detén `postgres_isam` antes de levantar los 3 nodos, o viceversa).

---

## 2. Configuración inicial y levantado de nodos

### 2.1. Crear el archivo `.env`

Copia el archivo de ejemplo y ajusta las credenciales si lo deseas (`.env` está ignorado por Git):

```bash
cp .env.example .env
```

Variables requeridas en `.env`:

| Variable | Descripción |
| :--- | :--- |
| `POSTGRES_USER` | Usuario administrador de PostgreSQL en los 3 nodos |
| `POSTGRES_PASSWORD` | Contraseña del usuario administrador |
| `POSTGRES_DB` | Nombre de la base de datos inicial en los 3 nodos |

Si falta `.env` o alguna de estas variables, Docker Compose detendrá la ejecución con un mensaje explícito.

### 2.2. Validar configuración y levantar los nodos

```bash
# Validar el archivo compose y las variables de .env
docker compose -f docker-compose.yml config

# Construir la imagen (postgres:18.6 + iproute2 + iputils-ping + herramientas ISAM) y levantar los 3 nodos
docker compose -f docker-compose.yml up -d --build
```

Comandos útiles de monitoreo y control:

```bash
# Ver estado y healthchecks de los contenedores
docker compose -f docker-compose.yml ps

# Ver logs en tiempo real
docker compose -f docker-compose.yml logs -f

# Detener los contenedores conservando los datos
docker compose -f docker-compose.yml down
```

---

## 3. Simulación y verificación de latencias de red

Los tres contenedores se conectan a la red bridge `pg_dist_net` (`172.25.0.0/24`) con IPs estáticas y capacidad `NET_ADMIN`.

### Topología y latencias configuradas

| Origen | Destino | IP destino | Delay de salida | RTT esperado (ida y vuelta) |
| :--- | :--- | :--- | :--- | :--- |
| `nodo_a` (`172.25.0.10`) | `nodo_b` | `172.25.0.20` | `10 ms` | **20 ms** (`A <-> B`) |
| `nodo_a` (`172.25.0.10`) | `nodo_c` | `172.25.0.30` | `20 ms` | **40 ms** (`A <-> C`) |
| `nodo_b` (`172.25.0.20`) | `nodo_a` | `172.25.0.10` | `10 ms` | **20 ms** (`A <-> B`) |
| `nodo_b` (`172.25.0.20`) | `nodo_c` | `172.25.0.30` | `12.5 ms` | **25 ms** (`B <-> C`) |
| `nodo_c` (`172.25.0.30`) | `nodo_a` | `172.25.0.10` | `20 ms` | **40 ms** (`A <-> C`) |
| `nodo_c` (`172.25.0.30`) | `nodo_b` | `172.25.0.20` | `12.5 ms` | **25 ms** (`B <-> C`) |

El tráfico hacia el host/gateway va por la banda 3 de `prio` (sin `netem`), de modo que las conexiones desde el host no sufren latencia artificial.

### Aplicar y verificar las latencias

```bash
# 1. Esperar healthchecks y aplicar reglas tc en los 3 nodos (idempotente)
./scripts/setup_latencies.sh

# 2. Verificar RTT promedio entre A->B (20 ms), A->C (40 ms) y B->C (25 ms) con tolerancia +/- 3 ms
./scripts/verify_latencies.sh
```

> **Importante sobre persistencia de `tc`:**
> Las reglas de `tc` viven en la pila de red en memoria de cada contenedor y **se pierden cada vez que reinicias o recreas los contenedores** (`docker compose -f docker-compose.yml restart`, `down`/`up`, reinicio de Docker). Cada vez que eso ocurra, debes volver a ejecutar `./scripts/setup_latencies.sh`.

---

## 4. Conexión desde el host y conexiones internas / FDW

### 4.1. Conexión desde el host (clientes externos, `psql`, DBeaver, Python)

Usa las credenciales definidas en `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) sobre `localhost`:

| Nodo | Host | Puerto del host | Ejemplo con `psql` |
| :--- | :--- | :--- | :--- |
| `nodo_a` | `localhost` | `5433` | `psql -h localhost -p 5433 -U postgres -d clinica_dist` |
| `nodo_b` | `localhost` | `5434` | `psql -h localhost -p 5434 -U postgres -d clinica_dist` |
| `nodo_c` | `localhost` | `5435` | `psql -h localhost -p 5435 -U postgres -d clinica_dist` |

### 4.2. Conexiones internas entre nodos (FDW / `postgres_fdw`)

> **Nota para el siguiente integrante (configuración de FDW y fragmentación):**
> - Las conexiones **internas** entre nodos (por ejemplo, al crear `SERVER` con `postgres_fdw` o `dblink`) deben usar siempre el **puerto interno `5432`**, **nunca** los puertos del host (`5433`, `5434`, `5435`).
> - Usa **preferiblemente las IPs estáticas** de la red `pg_dist_net` (`172.25.0.10` para `nodo_a`, `172.25.0.20` para `nodo_b`, `172.25.0.30` para `nodo_c`), ya que evitan cualquier problema de resolución DNS y coinciden directamente con los filtros `tc u32`.
> - Como alternativa, también se pueden usar los nombres de servicio Docker (`nodo_a`, `nodo_b`, `nodo_c`) siempre sobre el puerto `5432`.

---

## 5. Scripts de inicialización automática (`init-scripts/`)

Cada nodo monta en solo-lectura (`:ro`) el lanzador `init-scripts/00-run-all.sh` y sus carpetas de scripts:

- `init-scripts/common/`: scripts `.sql` y `.sh` que se ejecutan **primero** en los 3 nodos (en orden alfabético determinista con `LC_ALL=C`).
- `init-scripts/nodo_a/`, `init-scripts/nodo_b/`, `init-scripts/nodo_c/`: scripts `.sql` y `.sh` específicos de cada nodo, que se ejecutan **después** de `common/` (también en orden alfabético).
- Cualquier otro archivo (como `.gitkeep`) es ignorado.

Los scripts de inicialización solo corren automáticamente cuando el volumen de datos del nodo (`pgdata_a`, `pgdata_b`, `pgdata_c`) se inicializa por primera vez. Para forzar que se vuelvan a ejecutar desde cero:

```bash
docker compose -f docker-compose.yml down -v
docker compose -f docker-compose.yml up -d --build
./scripts/setup_latencies.sh
```

> **Advertencia:** `docker compose -f docker-compose.yml down -v` **elimina permanentemente los volúmenes nombrados (`pgdata_a`, `pgdata_b`, `pgdata_c`) y borra todos los datos de los tres nodos**. Úsalo únicamente cuando quieras reiniciar la base de datos por completo.

---

## 6. Troubleshooting

### Error `\r` o `bad interpreter` en Windows (saltos de línea CRLF)

Aunque `.gitattributes` fuerza `eol=lf` para `*.sh` y `*.sql`, si clonaste el repositorio antes de ese cambio o con `core.autocrlf=true` activo en Windows, los scripts pueden tener terminaciones CRLF y fallar con `\r: command not found` o `bad interpreter`. Para corregirlo:

```bash
git add --renormalize .
git checkout -- .
```

(Si el problema persiste en archivos ya modificados localmente, realiza un clon limpio del repositorio después de actualizar la rama.)

### Error de `tc` por módulos del kernel (`sch_netem` / `sch_prio`)

Si `./scripts/setup_latencies.sh` falla al ejecutar `tc`, verifica que Docker Desktop esté usando el backend **WSL2** actualizado (en Linux nativo, verifica que el paquete de módulos extra del kernel incluya `sch_netem` y `sch_prio`, por ejemplo `linux-modules-extra-$(uname -r)` en Ubuntu/Debian).

### Puerto `5433` ya en uso

Si `nodo_a` falla al iniciar porque el puerto `5433` está ocupado, comprueba si el contenedor `postgres_isam` de `compose.yml` está corriendo y detenlo con `docker compose -f compose.yml down`.
