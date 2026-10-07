FROM postgres:18.6

RUN apt-get update && \
    apt-get install -y \
        postgresql-server-dev-18 \
        gcc \
        make && \
    rm -rf /var/lib/apt/lists/*
