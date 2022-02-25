# SLATE Portal

This repository contains the online Portal to the [SLATE platform](https://slateci.io/) and uses [globus](https://docs.globus.org/) in order to authenticate users with the [Auth API](https://docs.globus.org/api/auth/).

## Local Development with Containers

### Requirements

#### Choose a Container Engine

Install **ONE** of the following for developing, managing, and running OCI containers on your system:

* [Docker](https://docs.docker.com/get-docker/)
* [Podman](https://podman.io/)

For the sake of simplicity this guide will focus on Docker (see [the podman docs](https://docs.podman.io/en/latest/Commands.html) for alternate syntax).

#### Create `portal.conf`

Create a blank file in the following place of this project: `instance/portal.conf`. Complete the steps described below to add properties and finalize this file.

#### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev, development, and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you'll be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you'll be asked for some information, including the redirect URL and any scopes you will be requesting.
  * Redirect URL: `http://localhost:5000/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `instance/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.

#### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* Specify the SLATE API server in the following place:
  * `instance/portal.conf` in the `SLATE_API_ENDPOINT` property.
* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied into this project in the following place:
  * `instance/portal.conf` in the `SLATE_API_TOKEN` property.

### Finalize `portal.conf`

Add these remaining properties to `instance/portal.conf` in this project:

* `DEBUG = True`
* `GLOBUS_AUTH_LOGOUT_URI = 'https://auth.globus.org/v2/web/logout'`
* ``SECRET_KEY = '=.DKwWzDd}!3}6yeAY+WTF#W:zt5msTI7]2`o}Y!ziU!#CYD+;T9JpW$ud|5C_3'``
* `SERVER_NAME = 'localhost:5000'`
* `SLATE_WEBSITE_LOGFILE = '/var/log/uwsgi/portal.log'`

At this point `instance/portal.conf` should resemble:

```properties
DEBUG = True
GLOBUS_AUTH_LOGOUT_URI = 'https://auth.globus.org/v2/web/logout'
PORTAL_CLIENT_ID = '<your-value>'
PORTAL_CLIENT_SECRET = '<your-value>'
SECRET_KEY = '=.DKwWzDd}!3}6yeAY+WTF#W:zt5msTI7]2`o}Y!ziU!#CYD+;T9JpW$ud|5C_3'
SERVER_NAME = 'localhost:5000'
SLATE_API_TOKEN = '<your-value>'
SLATE_API_ENDPOINT = 'https://api-dev.slateci.io:18080'
SLATE_WEBSITE_LOGFILE = '/var/log/uwsgi/portal.log'
```

### Build and Run Portal

Build the Docker image:

```shell
docker build -f Dockerfile -t slate-portal:local .
```

Running the image will create a new tagged container and start Portal:

```shell
[your@localmachine ~]$ docker run -it -v ${PWD}:/etc/slate/slate-website-python -p 5000:5000 slate-portal:local
 * Serving Flask app 'portal' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.2:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

Point your browser to `http://localhost:5000`.







#### Set up your environment.
* [OS X](#os-x)

#### Create your own App registration for use in the Portal. 
* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you'll be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you'll be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `https://localhost:5000/authcallback` (note: if using EC2 `localhost` should be replaced with the IP address of your instance).
    * Scopes: `urn:globus:auth:scope:transfer.api.globus.org:all`, `openid`, `profile`, `email`
* After creating your App the client id and secret can be copied into this project in the following two places:
    * `portal/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.
    * `service/service.conf` where the `PORTAL_CLIENT_ID` is used to validate the access token that the Portal sends to the Service.

### OS X

##### Environment Setup

* `sudo easy_install pip`
* `sudo pip install virtualenv`
* `sudo mkdir ~/projects`
* `cd ~/projects`
* `git clone https://github.com/slateci/slate-portal.git`
* `cd slate-portal`
* `virtualenv venv`
* `source venv/bin/activate`
* `pip install -r requirements.txt`
* `mkdir instance`
* `touch instance/portal.conf`
* Note that current `portal.conf` file located in `slate-portal/portal/portal.conf` is the default .conf file from the Globus Developer Portal. SLATE Portal will real from the new `instance/portal.conf` file.
* New `instance/portal.conf` file should be updated with new/correct API keys.

##### Running the Portal App

* `./run_portal.py`
* point your browser to `https://localhost:5000`
