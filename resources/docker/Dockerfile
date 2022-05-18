# syntax=docker/dockerfile:1

# Docker image build arguments:
ARG baseimage=centos:7
ARG port=5050
ARG virtualenv=/python3/venv

#######################################
## Local Stage                        #
#######################################
FROM ${baseimage} as local-stage

# Docker image build arguments:
ARG port
ARG virtualenv

# Docker container environmental variables:
ENV FLASK_PORT=${port}
ENV PATH=${virtualenv}/bin:$PATH

# Package installs/updates:
RUN yum install -y epel-release
RUN yum install -y boost \
    gcc \
    libcurl \
    libffi-devel \
    net-tools \
    openssl \
    python3-devel \
    which \
    zlib

# Change working directory:
WORKDIR /python3

# Configure a modern Python interpreter:
RUN pip3 install virtualenv
COPY ./resources/docker/requirements.txt ./requirements.txt
RUN bash -c "virtualenv --python=/usr/bin/python3 venv && source ${virtualenv}/bin/activate && pip install --no-cache-dir -r ./requirements.txt"

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
ARG virtualenv

# Docker container environmental variables:
ENV FLASK_PORT=${port}
ENV PATH=${virtualenv}/bin:$PATH

# Package installs/updates:
RUN yum install -y epel-release
RUN yum install -y boost \
    gcc \
    libcurl \
    libffi \
    net-tools \
    openssl \
    python3 \
    which \
    zlib
RUN yum clean all && rm -rf /var/cache/yum

# Configure a modern Python interpreter:
RUN pip3 install virtualenv
COPY --from=local-stage /python3 /python3

# Change working directory:
WORKDIR /slate

# Copy in relevant source material:
COPY ./portal ./portal
COPY ./run_portal.py ./run_portal.py

# Create instance directory:
RUN mkdir ./instance

# Ports:
EXPOSE ${port}

# Volumes:
VOLUME [ "/slate/instance" ]

# Run once the container has started:
ENTRYPOINT [ "python /slate/run_portal.py" ]
