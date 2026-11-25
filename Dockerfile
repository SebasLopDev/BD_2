FROM postgres:18.6

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-server-dev-18 \
        gcc \
        make \
        iproute2 \
        iputils-ping && \
    rm -rf /var/lib/apt/lists/*
