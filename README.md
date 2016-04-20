# Modern Research Data Portal
Simple web app framework for the exercises in the GlobusWorld developer workshop.

## Overview
This repository contains two separate server applications. The first, the "Portal," is an example "research portal"
that demonstrates how to authenticate users with Globus Auth, how to make requests against the Globus Transfer API, and how to interact with an HTTPS-enabled Globus Endpoint. All of the Portal code can be found in the `portal/` directory.

The second application, the "Service," is an example "resource server" that demonstrates how a research portal can offload tasks to a separate service that has the capability to perform tasks on behalf of users. All of the Service code can be found in the 'service/' directory.

## Getting Started

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

### Globus-Provided AWS Instance

At the Globus World workshop, you will be given an IP address, username, and
password. Using these, open an ssh connection to the remote instance.

Once connected, run the commands below, substituting `YOUR_IP` as required.

##### Environment Setup

* `git clone https://github.com/globus/globus-sample-data-portal`
* `cd globus-sample-data-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `sed -i 's/localhost/0.0.0.0/' run_*.py`
* `sed -i '4,//s/localhost/YOUR_IP/' */*.conf`

##### Running the Portal App

* `./run_portal.py`
* point your web browser to `https://YOUR_IP:5000/`

##### Running the Service App

* `./run_service.py`
* API is located at `https://localhost:5100/api`
