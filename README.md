# SLATE Portal

This repository contains the web Portal to the [SLATE platform](https://slateci.io/) and the associated Ansible playbook used for server deployments.

## Application Framework

Portal is written using the Flask framework and makes use of uWSGI on the development and production environments.
* [Flask](https://flask.palletsprojects.com/en/2.0.x/) is a micro framework for web applications written in Python.
* [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) is a software app providing a Web Server Gateway Interface.

## Authentication Layer

[globus](https://docs.globus.org/) is used to authenticate users with the [Auth API](https://docs.globus.org/api/auth/) (see [notebook/README.md](notebook/README.md) for additional information).

## Development/Deployment

Several methods for application development and Ansible playbook deployment exist and are described at length in the [related documentation](docs/index.md).

## Resources

* [Flask: Quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
* [Quickstart for Python/WSGI applications](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)
