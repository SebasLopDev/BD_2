# Base de Datos II - Implementación de ISAM

Proyecto desarrollado para el curso de **Base de Datos II**.

El proyecto implementa una estructura de índice **ISAM (Indexed Sequential Access Method)** utilizando lenguaje C e integrándola con PostgreSQL mediante una extensión nativa.

## 📌 Descripción

El proyecto tiene como objetivo implementar y probar un índice ISAM sobre los registros de la tabla `paciente` de una base de datos PostgreSQL.

La implementación permite:

- Construir un índice ISAM a partir de los registros existentes.
- Organizar los registros en páginas de datos.
- Utilizar un índice estático para localizar las páginas.
- Realizar búsquedas mediante una clave.
- Insertar registros en la estructura ISAM en memoria.
- Manejar páginas de desbordamiento (*overflow*).
- Integrar las operaciones mediante funciones nativas de PostgreSQL.
- Consultar estadísticas y visualizar las páginas del índice.
- Comprobar determinadas condiciones de integridad de la estructura.
- Ejecutar el entorno de desarrollo mediante Docker.

## 🛠️ Tecnologías utilizadas

- **C** para la implementación de la estructura ISAM.
- **PostgreSQL 18.6** como sistema gestor de bases de datos.
- **Docker y Docker Compose** para configurar el entorno.
- **Make y PGXS** para compilar e instalar la extensión.
- **Python y Flask** para la aplicación web del proyecto.
- **HTML y CSS** para la interfaz web.
- **Git y GitHub** para el control de versiones.

## 📁 Estructura del proyecto

La estructura principal del repositorio es la siguiente:

```text
BD_2/
│
├── isam_extension/
│   ├── isam.c
│   ├── isam_core.h
│   ├── construccion.c
│   ├── busqueda.c
│   ├── insercion.c
│   ├── Makefile
│   ├── isam.control
│   └── isam--1.0.sql
│
├── templates/
├── static/
├── app.py
├── bd.py
├── consultas.py
├── tabla.sql
├── tablaNuevaMsql.sql
├── tablasPostgre.sql
├── requirements.txt
├── Dockerfile
├── compose.yml
├── .gitignore
└── README.md
```

### Archivos principales de la extensión ISAM

| Archivo | Descripción |
|---|---|
| `isam_core.h` | Define las estructuras de datos y las declaraciones de las funciones compartidas. |
| `construccion.c` | Construye el índice a partir de los registros de la tabla `paciente`. |
| `busqueda.c` | Localiza la página correspondiente a una clave mediante el índice estático. |
| `insercion.c` | Implementa la inserción de registros y el manejo de páginas de overflow. |
| `isam.c` | Expone las operaciones de la estructura mediante funciones nativas invocables desde SQL. |
| `isam--1.0.sql` | Define las funciones SQL que proporciona la extensión. |
| `isam.control` | Contiene los metadatos necesarios para registrar la extensión en PostgreSQL. |
| `Makefile` | Configura la compilación e instalación mediante PGXS. |

## ⚙️ Requisitos

Para ejecutar el proyecto se necesita:

- Git.
- Docker.
- Docker Compose.
- Un sistema operativo compatible con Docker.

El entorno de PostgreSQL y las herramientas necesarias para compilar la extensión se configuran dentro del contenedor mediante el `Dockerfile`.

## 🚀 Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/SebasLopDev/BD_2.git
cd BD_2
```

### 2. Construir e iniciar el contenedor

Desde la raíz del proyecto, ejecutar:

```bash
sudo docker compose up -d --build
```

Verificar que el contenedor esté ejecutándose:

```bash
sudo docker ps
```

El contenedor de PostgreSQL utilizado por el proyecto se llama:

```text
postgres_isam
```

### 3. Verificar PostgreSQL

Consultar la versión del servidor:

```bash
sudo docker exec postgres_isam \
  psql -U postgres -d clinica \
  -c "SELECT version();"
```

### 4. Configurar la base de datos

Para cargar el esquema de PostgreSQL, ejecutar desde la raíz del repositorio:

```bash
sudo docker exec -i postgres_isam \
  psql -U postgres -d clinica < tablasPostgre.sql
```

**Nota:** ejecutar este paso según el estado de la base de datos. Si las tablas ya existen, la ejecución podría producir errores de objetos duplicados.

Para ingresar directamente a PostgreSQL:

```bash
sudo docker exec -it postgres_isam \
  psql -U postgres -d clinica
```

### 5. Compilar e instalar la extensión ISAM

Ingresar al contenedor:

```bash
sudo docker exec -it postgres_isam bash
```

Dentro del contenedor, ejecutar:

```bash
cd /isam_extension
make clean
make
make install
```

Estos comandos compilan los módulos C e instalan la biblioteca y los archivos de la extensión en el entorno PostgreSQL del contenedor.

Si se modifican los archivos fuente, se debe volver a compilar e instalar la extensión para que los cambios estén disponibles en PostgreSQL.

### 6. Registrar la extensión

Desde `psql`, ejecutar:

```sql
CREATE EXTENSION IF NOT EXISTS isam;
```

El archivo `isam--1.0.sql` debe contener las declaraciones de las funciones que se instalarán automáticamente.

Si la extensión ya estaba instalada y se agregaron nuevas funciones, estas deberán registrarse en la base de datos o incorporarse mediante un mecanismo de actualización de la extensión.

## 🔧 Funcionamiento de la extensión ISAM

La extensión utiliza funciones nativas de PostgreSQL implementadas en C. Estas funciones permiten ejecutar las operaciones de la estructura ISAM directamente desde consultas SQL.

### Construcción del índice

La función `isam_build()` construye el índice a partir de los registros existentes en la tabla `paciente`.

Para acceder a los datos se utiliza SPI (*Server Programming Interface*), que permite ejecutar consultas SQL desde funciones nativas de PostgreSQL.

La consulta obtiene los identificadores y nombres de los pacientes, ordenados por `id_paciente`. Después, los registros se distribuyen en páginas de datos con una capacidad máxima de 50 registros por página.

La función devuelve la cantidad de páginas principales creadas.

### Búsqueda de registros

La función `isam_search(integer)` recibe una clave y busca el registro correspondiente en la estructura ISAM.

El proceso utiliza `buscar_pagina()` para localizar la página principal apropiada mediante búsqueda binaria sobre las entradas del índice. Posteriormente, se examinan los registros de esa página y, si es necesario, sus páginas de overflow.

Si encuentra la clave, devuelve el dato asociado. Si no encuentra el registro, devuelve `NULL`.

### Inserción de registros

La función `isam_insert(integer, text)` permite solicitar la inserción de un registro en la estructura ISAM.

La función prepara el registro y delega la operación a la lógica de inserción, que busca la página correspondiente, incorpora el registro y contempla el uso de páginas de overflow cuando una página está llena.

**Limitación importante:** los registros insertados mediante `isam_insert()` se almacenan en la estructura ISAM en memoria. Esta operación no inserta automáticamente el registro en la tabla `paciente`.

Por tanto, la inserción en ISAM y la inserción persistente en la tabla PostgreSQL son operaciones distintas en la implementación actual.

### Gestión de memoria

La estructura del índice utiliza un contexto de memoria específico de PostgreSQL para conservar sus páginas entre llamadas SQL dentro del mismo backend.

Esto permite mantener los cambios de la estructura durante la vida de ese proceso. Sin embargo, no representa almacenamiento persistente en disco ni memoria compartida automáticamente entre todos los procesos de PostgreSQL.

La estructura puede perderse al reiniciar el servidor o al reconstruir el índice mediante `isam_build()`.

## 🧩 Funciones SQL disponibles

Una vez compiladas e instaladas las funciones correspondientes, las operaciones pueden ejecutarse desde PostgreSQL.

| Función | Descripción |
|---|---|
| `isam_build()` | Construye el índice ISAM a partir de la tabla `paciente`. |
| `isam_search(integer)` | Busca un registro por su clave. |
| `isam_insert(integer, text)` | Inserta un registro en la estructura ISAM en memoria. |
| `isam_stats()` | Muestra estadísticas de las páginas y los registros del índice. |
| `isam_show_pages()` | Muestra las páginas del índice, sus registros y sus enlaces de overflow. |
| `isam_validate()` | Comprueba determinadas condiciones de integridad de la estructura. |

Las tres funciones de diagnóstico deben estar implementadas, compiladas y registradas en PostgreSQL para poder utilizarlas.

## 🔎 Ejemplos de uso

Los siguientes ejemplos se ejecutan desde `psql`, una vez que las funciones estén instaladas y registradas.

### 1. Construir el índice

```sql
SELECT isam_build();
```

La función devuelve el número de páginas principales creadas a partir de los registros de la tabla `paciente`.

### 2. Buscar un registro

```sql
SELECT isam_search(1);
```

Si existe un registro con esa clave, la función devuelve su dato asociado.

Por ejemplo, si el nombre almacenado para la clave `1` es `Paciente1`, el resultado será:

```text
Paciente1
```

Si la clave no existe:

```sql
SELECT isam_search(999999);
```

El resultado será:

```text
NULL
```

### 3. Insertar un registro en ISAM

```sql
SELECT isam_insert(900001, 'PruebaISAM');
```

Para consultar el registro en la estructura ISAM:

```sql
SELECT isam_search(900001);
```

Resultado esperado:

```text
PruebaISAM
```

Este ejemplo modifica la estructura ISAM en memoria, pero no inserta automáticamente el registro en la tabla `paciente`.

### 4. Consultar estadísticas

```sql
SELECT isam_stats();
```

La función informa sobre el número de páginas principales, páginas de overflow, páginas totales y registros contabilizados.

### 5. Visualizar las páginas

```sql
SELECT isam_show_pages();
```

La función muestra las páginas principales y las páginas de overflow, junto con las claves y los datos que contienen.

### 6. Validar la estructura

```sql
SELECT isam_validate();
```

La función comprueba determinadas condiciones de integridad, como los límites de los contadores, el orden de las claves dentro de cada página y la presencia de ciclos en las cadenas de overflow.

Esta validación no garantiza todas las propiedades posibles de un índice ISAM.

## 🧪 Datos de prueba

Para cargar registros de prueba en la tabla `paciente`, se puede utilizar la siguiente consulta, siempre que la tabla esté vacía o se haya verificado que no habrá conflictos con los datos existentes:

```sql
INSERT INTO paciente
(nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email)
SELECT
    'Paciente' || g,
    'Prueba',
    (70000100 + g)::varchar,
    DATE '2000-01-01' + (g % 500),
    CASE WHEN g % 2 = 0 THEN 'M' ELSE 'F' END,
    '999' || LPAD(g::varchar, 6, '0'),
    'Arequipa',
    'paciente' || g || '@test.com'
FROM generate_series(1, 120) AS g;
```

Esta consulta genera 120 registros de prueba en la tabla PostgreSQL.

Después de cargar los datos, se puede construir el índice:

```sql
SELECT isam_build();
```

De esta manera, la estructura ISAM se construye utilizando los registros persistentes de la tabla.

Para probar las inserciones y el overflow de la estructura en memoria, se pueden ejecutar llamadas a `isam_insert()` con claves que no interfieran con las utilizadas por los datos de prueba.

## 🧩 Funcionamiento general

El flujo general de construcción y búsqueda del índice es el siguiente:

```text
        Tabla paciente
      (datos persistentes)
               |
               v
      Construcción del índice
          isam_build()
               |
               v
         Índice estático
               |
               v
         Páginas de datos
          /     |     \
         v      v      v
      Página 1 Página 2 Página 3
                         |
                         v
                  Páginas overflow
```

El índice almacena la primera clave de cada página principal y un puntero hacia ella. Durante una búsqueda, se utiliza el índice estático para determinar la página candidata. A continuación, se recorren sus registros y, cuando corresponde, sus páginas de overflow.

Las inserciones mediante `isam_insert()` modifican la estructura en memoria y no actualizan automáticamente la tabla persistente.

## 🐳 Docker

El proyecto utiliza Docker para mantener un entorno de desarrollo reproducible.

La configuración del contenedor permite disponer de PostgreSQL y de las herramientas necesarias para compilar la extensión nativa.

El entorno incluye los componentes de desarrollo correspondientes a PostgreSQL 18, junto con GCC y Make, según la configuración del `Dockerfile`.

El directorio de la extensión se utiliza para compilar los módulos C dentro del entorno preparado para el proyecto.

## 👥 Participantes

Proyecto desarrollado para el curso de **Base de Datos II**.

- ALONZO ESTEFANO CUELA RODRIGUEZ
- SEBASTIAN JOSE LOPEZ PEÑA
- EDGARD EDWARD RODRIGUEZ VILCAPAZA
- GONZALO NICOLAS SUMINA QUISPE
- BARUA PROJOY
- MARIA BELEN CALLE PINTO

## 📄 Licencia

Proyecto académico desarrollado con fines educativos.
