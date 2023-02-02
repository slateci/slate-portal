# SLATE Portal

[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)
[![Integration Tests](https://github.com/slateci/slate-portal/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/slateci/slate-portal/actions/workflows/integration-tests.yml)
[![Deploy: PROD](https://github.com/slateci/slate-portal/actions/workflows/deploy-prod.yml/badge.svg?branch=master)](https://github.com/slateci/slate-portal/actions/workflows/deploy-prod.yml)

This repository contains the web Portal to the [SLATE platform](https://slateci.io/) and the Helm Chart used for the Google Cloud Platform deployments.

## Application Framework

Portal is written with the Flask framework and makes use of a Web Server Gateway Interface (WSGI).
* [Flask](https://flask.palletsprojects.com/en/2.0.x/) is a micro framework for web applications written in Python.
* [Werkzeug](https://werkzeug.palletsprojects.com/en/2.2.x/) is a Python WSGI web application library built into Flask and provides a local debugging environment.
    * E.g. `app.run(<args>)`
* [Gunicorn](https://docs.gunicorn.org/en/stable/) is a Python WSGI web application server used by our various deployment environments.

## Authentication Layer

[globus](https://docs.globus.org/) is used to authenticate users with the [Auth API](https://docs.globus.org/api/auth/). Read more at [notebook/README.md](resources/notebook/README.md).

## Local Development

See [Local Development with Containers](resources/docs/container.md) for more details.

## Deployment

See [Deployment Steps](https://docs.google.com/document/d/1WBrVPhvCGxAWbXaxDbaKQ2J73K6amF4fbXRxzvtGwSo/edit#heading=h.6rq3vs2f6vdu) for more details.

## Resources

* [Flask: Quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
* [Quickstart for Python/WSGI applications](https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html)
