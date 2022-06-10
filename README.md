# SLATE Portal

[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[![Integration Tests](https://github.com/slateci/slate-portal/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/slateci/slate-portal/actions/workflows/integration-tests.yml)

This repository contains the web Portal to the [SLATE platform](https://slateci.io/) and the associated Ansible playbook used for server deployments.

## Application Framework

Portal is written with the Flask framework and makes use of uWSGI on the development and production environments.
* [Flask](https://flask.palletsprojects.com/en/2.0.x/) is a micro framework for web applications written in Python.
* [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) is a software app providing a Web Server Gateway Interface.

## Authentication Layer

[globus](https://docs.globus.org/) is used to authenticate users with the [Auth API](https://docs.globus.org/api/auth/) (see [notebook/README.md](resources/notebook/README.md) for additional information).

## Development/Deployment

Several methods for local application development and deployment via Ansible playbook exist and are described at length in the [related documentation](resources/docs/index.md).

## Resources

* [Flask: Quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
* [Quickstart for Python/WSGI applications](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)
