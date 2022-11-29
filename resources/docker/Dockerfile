# syntax=docker/dockerfile:1

# Docker image build arguments:
ARG baseimage=rockylinux:9
ARG port=5050

#######################################
## Local Stage                        #
#######################################
FROM ${baseimage} as local-stage

# Docker image build arguments:
ARG port

# Docker container environmental variables:
ENV FLASK_PORT=${port}

# Package installs/updates:
RUN dnf install -y epel-release
RUN dnf install -y \
    boost \
    gcc \
    libcurl \
    libffi-devel \
    net-tools \
    openssl \
    python3-devel \
    which \
    zlib

# Change working directory:
WORKDIR /tmp

# Install Python packages:
COPY ./resources/docker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt && \
    rm ./requirements.txt

# Change working directory:
WORKDIR /slate

# Ports:
EXPOSE ${port}

# Volumes:
VOLUME [ "/slate" ]

#######################################
## Release Stage                      #
#######################################

FROM ${baseimage} as release-stage

# Docker image build arguments:
ARG port

# Docker container environmental variables:
ENV FLASK_PORT=${port}

# Package installs/updates:
RUN dnf install -y epel-release
RUN dnf install -y \
    boost \
    gcc \
    libcurl \
    libffi-devel \
    net-tools \
    openssl \
    which \
    zlib
RUN dnf clean all && \
    rm -rf /var/cache/yum

# Prepare entrypoint:
COPY ./resources/docker/scripts/docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

# Change working directory:
WORKDIR /tmp

# Install Python packages:
COPY ./resources/docker/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt && \
    rm ./requirements.txt

# Change working directory:
WORKDIR /slate

# Copy in relevant source material:
COPY ./portal ./portal
COPY ./run_portal.py ./run_portal.py

# Create instance directory:
RUN mkdir ./instance

# Ports:
EXPOSE ${port}

# Run once the container has started:
ENTRYPOINT [ "/docker-entrypoint.sh" ]
