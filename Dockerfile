FROM postgres:18.6

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        postgresql-server-dev-18 \
        gcc \
        make \
        iproute2 \
        iputils-ping && \
    rm -rf /var/lib/apt/lists/*

COPY isam_extension /tmp/isam_extension
RUN sed -i 's/\r$//' /tmp/isam_extension/Makefile /tmp/isam_extension/isam.control /tmp/isam_extension/isam--1.0.sql && \
    make -C /tmp/isam_extension with_llvm=no clean && \
    make -C /tmp/isam_extension with_llvm=no && \
    make -C /tmp/isam_extension with_llvm=no install && \
    rm -rf /tmp/isam_extension
