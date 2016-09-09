# Modern Research Data Portal
Simple web app framework demonstrating how to build a data portal using
the Globus [platform](https://www.globus.org/platform).

## Overview
This repository contains two separate server applications. The first, the "Portal," is an example "research portal"
that demonstrates how to authenticate users with Globus [Auth](https://docs.globus.org/api/auth/), how to make requests against the Globus [Transfer API](https://docs.globus.org/api/transfer/), and how to interact with an HTTPS-enabled Globus Endpoint. All of the Portal code can be found in the `portal/` directory.

The second application, the "Service," is an example "resource server" that demonstrates how a research portal can offload tasks to a separate service that has the capability to perform tasks on behalf of users. All of the Service code can be found in the `service/` directory.

## Getting Started
* Set up your environment.
    * [OS X](#os-x)
    * [Linux](#linux-ubuntu)
    * [Windows](#windows)
* Create your own App registration for use in the Portal. Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.

### OS X

##### Environment Setup

* `sudo easy_install pip`
* `sudo pip install virtualenv`
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `./run_portal.py`
* point your browser to `https://localhost:5000`

##### Running the Service App

* `./run_service.py`
* API is located at `https://localhost:5100/api`

### Linux (Ubuntu)

##### Environment Setup

* `sudo apt-get update`
* `sudo apt-get install python-pip`
* `sudo pip install virtualenv`
* `sudo apt-get install git`
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `./run_portal.py`
* point your browser to `https://localhost:5000`

##### Running the Service App

* `./run_service.py`
* API is located at `https://localhost:5100/api`

### Windows

##### Environment Setup

* Install Python (<https://www.python.org/downloads/windows/>)
* `pip install virtualenv`
* Install git (<https://git-scm.com/downloads>)
* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `venv\Scripts\activate`
* `pip install -r requirements.txt`

##### Running the Portal App

* `python run_portal.py`
* point your browser to `https://localhost:5000`

##### Running the Service App

* `python run_service.py`
* API is located at `https://localhost:5100/api`
