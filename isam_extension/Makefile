EXTENSION = isam

MODULE_big = isam

OBJS = isam.o construccion.o busqueda.o insercion.o

DATA = isam--1.0.sql

PG_CONFIG = pg_config

PGXS := $(shell $(PG_CONFIG) --pgxs)

include $(PGXS)
