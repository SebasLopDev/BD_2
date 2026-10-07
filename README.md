# Base de Datos II - Implementación de ISAM

Proyecto desarrollado para el curso de **Base de Datos II**.
El proyecto implementa una estructura de índice **ISAM (Indexed Sequential Access Method)** utilizando **C** e integrándola con **PostgreSQL** mediante una extensión.

## 📌 Descripción

El proyecto tiene como objetivo implementar y probar un índice ISAM sobre la tabla `paciente` de una base de datos PostgreSQL.

La implementación permite:

* Construir un índice ISAM a partir de los registros existentes.
* Organizar los registros en páginas de datos.
* Utilizar un índice estático para localizar las páginas.
* Realizar búsquedas mediante una clave.
* Manejar páginas de desbordamiento (`overflow`).
* Integrar la implementación en PostgreSQL mediante una extensión en C.
* Ejecutar el proyecto dentro de un contenedor Docker.

## 🛠️ Tecnologías utilizadas

* **C**
* **PostgreSQL 18.6**
* **Docker / Docker Compose**
* **Make / PGXS**
* **Git / GitHub**
* **Python / Flask** para la aplicación web del proyecto

## 📁 Estructura del proyecto

```text
BD_2-main/
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
├── tablasPostgre.sql
├── compose.yml
├── Dockerfile
├── app.py
├── bd.py
├── requirements.txt
└── README.md
```

## ⚙️ Requisitos

Para ejecutar el proyecto se necesita:

* Git
* Docker
* Docker Compose

No es necesario instalar PostgreSQL ni las herramientas de desarrollo de PostgreSQL directamente en el sistema anfitrión, ya que se instalan dentro del contenedor mediante el `Dockerfile`.

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/SebasLopDev/BD_2.git
cd BD_2-main
```

### 2. Levantar el contenedor

```bash
sudo docker compose up -d --build
```

Verificar que el contenedor esté ejecutándose:

```bash
sudo docker ps
```

El contenedor utilizado por el proyecto se llama:

```text
postgres_isam
```

### 3. Verificar PostgreSQL

```bash
sudo docker exec postgres_isam psql -U postgres -d clinica -c "SELECT version();"
```

## 🗄️ Configuración de la base de datos

Para cargar las tablas de la base de datos:

```bash
sudo docker exec -i postgres_isam psql -U postgres -d clinica < tablasPostgre.sql
```

Ingresar a PostgreSQL:

```bash
sudo docker exec -it postgres_isam psql -U postgres -d clinica
```

## 🔧 Compilación de la extensión ISAM

Ingresar al contenedor:

```bash
sudo docker exec -it postgres_isam bash
```

Luego:

```bash
cd /isam_extension
make clean
make
make install
```

La extensión contiene los siguientes módulos principales:

* `construccion.c`: construcción del índice ISAM a partir de los registros de la tabla.
* `busqueda.c`: búsqueda de la página correspondiente mediante el índice.
* `insercion.c`: inserción de registros y manejo de páginas de overflow.
* `isam.c`: funciones que permiten utilizar el índice desde PostgreSQL.
* `isam_core.h`: estructuras y declaraciones compartidas.

## 📦 Crear la extensión en PostgreSQL

Desde PostgreSQL:

```sql
CREATE EXTENSION isam;
```

## 🔎 Pruebas

Para construir el índice:

```sql
SELECT isam_build();
```

La función devuelve la cantidad de páginas utilizadas por el índice.

Para buscar un paciente por su `id_paciente`:

```sql
SELECT isam_search(3);
```

Por ejemplo, si el paciente con ID `3` tiene como nombre `Carlos`, el resultado será:

```text
Carlos
```

Si la clave no existe:

```sql
SELECT isam_search(999);
```

El resultado será:

```text
NULL
```

## 🧪 Datos de prueba

Para realizar pruebas con una cantidad mayor de registros se pueden insertar datos mediante:

```sql
INSERT INTO paciente
(nombre, apellido, dni, fecha_nacimiento, sexo, telefono, direccion, email)
SELECT
    'Paciente' || g,
    'Prueba',
    (70000100 + g)::varchar,
    '2000-01-01'::date + (g % 500),
    CASE WHEN g % 2 = 0 THEN 'M' ELSE 'F' END,
    '999' || LPAD(g::varchar, 6, '0'),
    'Arequipa',
    'paciente' || g || '@test.com'
FROM generate_series(1, 120) AS g;
```

Esto permite probar el funcionamiento del índice con varios registros y más de una página de datos.

## 🧩 Funcionamiento general

El funcionamiento básico del índice es:

```text
Tabla paciente
      │
      ▼
Construcción del índice
      │
      ▼
Índice estático
      │
      ▼
Páginas de datos
      │
      ├── Página 1
      ├── Página 2
      ├── Página 3
      └── ...
             │
             ▼
       Páginas overflow
```

El índice almacena la primera clave de cada página y un puntero hacia dicha página. Para realizar una búsqueda, primero se utiliza el índice para determinar la página donde debería encontrarse la clave. Luego se recorren los registros de la página y, si es necesario, sus páginas de overflow.

## 🐳 Docker

El proyecto utiliza Docker para mantener un entorno reproducible.

El `Dockerfile` instala:

* PostgreSQL 18.6
* PostgreSQL Server Development 18
* GCC
* Make

El código de `isam_extension` se monta dentro del contenedor para poder compilar la extensión directamente.

## 👥 Autores

Proyecto desarrollado para el curso de **Base de Datos II**.

* Gonzalo
* Sebastián

## 📄 Licencia

Proyecto académico desarrollado con fines educativos.

