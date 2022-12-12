# syntax=docker/dockerfile:1

# Docker image build arguments:
ARG baseimage=rockylinux:9
ARG port=5050

#######################################
## Base Stage                         #
#######################################
FROM ${baseimage} as base-stage

# Image build arguments:
ARG port

# Container environmental variables:
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

# Ports:
EXPOSE ${port}

# Run once the container has started:
ENTRYPOINT [ "/docker-entrypoint.sh" ]

#######################################
## Local Stage                        #
#######################################
FROM base-stage as local-stage

# Container environmental variables:
ENV FLASK_ENV=development

# Volumes:
VOLUME [ "/slate" ]

#######################################
## Release Stage                      #
#######################################
FROM base-stage as release-stage

# Container environmental variables:
ENV FLASK_ENV=production

# Package cache cleanup:
RUN dnf clean all && \
    rm -rf /var/cache/yum

# Copy in relevant source material:
COPY ./portal ./portal
COPY ./run_portal.py ./run_portal.py

# Create instance directory:
RUN mkdir ./instance
