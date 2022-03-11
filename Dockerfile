# syntax=docker/dockerfile:1
FROM centos:7

# Docker container environmental variables:
ENV DEBUG=False
ENV FLASK_PORT=5000

# Package installs/updates:
RUN yum install -y epel-release
RUN yum install -y which boost zlib openssl libcurl openssl gcc libffi-devel net-tools python3-devel

# Prepare entrypoint:
COPY docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

# Make logging directory:
RUN mkdir /var/log/uwsgi

# Change working directory:
WORKDIR /etc/slate

# Configure a modern Python interpreter:
RUN pip3 install virtualenv
COPY requirements.txt /tmp/requirements.text
RUN bash -c 'virtualenv --python=/usr/bin/python3 venv && source venv/bin/activate && pip install --no-cache-dir -r /tmp/requirements.text'

# Change working directory:
WORKDIR /etc/slate/slate-website-python

# Ports:
EXPOSE ${FLASK_PORT}

# Volumes
VOLUME [ "/etc/slate/slate-website-python/" ]

# Run once the container has started:
ENTRYPOINT [ "/docker-entrypoint.sh" ]
