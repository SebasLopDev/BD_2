🏥 Clínica Médica – Proyecto Flask + Base de Datos
1. Tecnologías
Python 3.x
Flask
PostgreSQL 18.6
Docker / Docker Compose
C
Extensión nativa de PostgreSQL para ISAM
🚀 Inicialización del proyecto en una máquina nueva
1. Clonar el proyecto

Primero clonar el repositorio:

git clone <URL_DEL_REPOSITORIO>

Entrar al proyecto:

cd BD_2-main

Comprobar que existen los archivos principales:

ls

Debe aparecer, entre otros:

compose.yml
isam_extension
tablasPostgre.sql
2. Comprobar Docker

Verificar si Docker está instalado:

sudo docker --version

Y Docker Compose:

sudo docker compose version

Si alguno de los dos no existe, hay que instalar Docker antes de continuar.

3. Levantar PostgreSQL

Este comando debe ejecutarse desde la raíz del proyecto, donde está compose.yml:

sudo docker compose up -d

Comprobar que el contenedor está funcionando:

sudo docker ps

Debe aparecer:

postgres_isam
4. Comprobar PostgreSQL

Ejecutar:

sudo docker exec postgres_isam psql -U postgres -d clinica -c "SELECT version();"

Debe mostrar PostgreSQL 18.6.

También podemos comprobar que la carpeta de la extensión está montada:

sudo docker exec postgres_isam ls /isam_extension

Deberían aparecer archivos como:

Makefile
isam.c
isam_core.h
construccion.c
busqueda.c
insercion.c
isam.control
isam--1.0.sql
5. Entrar al contenedor
sudo docker exec -it postgres_isam bash

Entrar a la carpeta:

cd /isam_extension

Importante: dentro del contenedor la ruta es:

/isam_extension

No ~/isam_extension.

6. Instalar herramientas de compilación

Dentro del contenedor:

apt update

Luego:

apt install -y postgresql-server-dev-18 gcc make

Comprobar:

gcc --version

y:

pg_config --version

Debe indicar PostgreSQL 18.x.

7. Compilar la extensión ISAM

Desde:

/isam_extension

ejecutar:

make clean

Luego:

make

Si no aparece ningún error:

make install
8. Comprobar que la extensión fue instalada

Todavía dentro del contenedor:

ls -l /usr/lib/postgresql/18/lib/isam.so

También:

ls -l /usr/share/postgresql/18/extension/isam*

Deberían existir:

isam.so
isam.control
isam--1.0.sql

Luego salir:

exit
9. Entrar a PostgreSQL
sudo docker exec -it postgres_isam psql -U postgres -d clinica
10. Crear la estructura de la base de datos

En una máquina nueva, la base estará vacía.

Desde Ubuntu, fuera de psql, ejecutar:

sudo docker exec -i postgres_isam psql -U postgres -d clinica < tablasPostgre.sql

Esto crea las tablas del sistema.

Comprobar:

sudo docker exec -it postgres_isam psql -U postgres -d clinica

Y:

\dt

Deberían aparecer las tablas de la clínica, incluyendo:

paciente
medico
cita
historial_medico
...
11. Comprobar los datos

El archivo tablasPostgre.sql solo crea las tablas, no los datos.

Por eso:

SELECT COUNT(*) FROM paciente;

puede devolver:

0

Para una demostración del ISAM se deben cargar datos de prueba o importar el dataset real del proyecto.

12. Crear la extensión ISAM

Dentro de psql:

CREATE EXTENSION isam;

Comprobar:

\df isam*

Deberían aparecer:

isam_build
isam_search
13. Construir el índice

Una vez que paciente tenga datos:

SELECT isam_build();

El resultado indica el número de páginas construidas.

Por ejemplo, con:

125 registros

y:

MAX_RECORDS = 50

se esperan:

3 páginas
14. Probar una búsqueda

Si existe un paciente con ID 3:

SELECT isam_search(3);

Debe devolver su nombre.

Por ejemplo:

 Carlos

Probar una clave inexistente:

SELECT isam_search(9999);

Debe devolver:

NULL
15. Detener el proyecto

Cuando termine el laboratorio:

sudo docker compose down

Esto detiene y elimina el contenedor, pero el volumen postgres_data permanece.

Por eso, si posteriormente ejecutas:

sudo docker compose up -d

los datos de PostgreSQL deberían seguir ahí.
