# Local Development with Containers

A containerized Portal will provide a near live-preview developer experience.

## Requirements

### Install Docker or Podman

* Install [Docker](https://docs.docker.com/get-docker/) to make use of the simpler `docker-compose` commands (if desired).
* For those that prefer Podman, install [Podman](https://podman.io/) and refer to the `podman` commands described below.

### Create `portal.conf`

Copy `instance/portal.conf.tmpl` to the following place in this project: `instance/portal.conf`. Complete the steps described below to modify properties and finalize this file.

### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev, development, and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `http://localhost:5050/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `instance/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.

### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* Specify the SLATE API server in the following place of this project:
    * `instance/portal.conf` in the `SLATE_API_ENDPOINT` property.
* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied to the following place in this project:
    * `instance/portal.conf` in the `SLATE_API_TOKEN` property.

### Select a mailgun API Token

Portal communicates with users via email with [mailgun](https://www.mailgun.com/).
* Ask the team for an appropriate API token.
* Once in hand the token can be copied to the following place in this project:
  * `instance/portal.conf` in the `MAILGUN_API_TOKEN` property. 

## Finalize `portal.conf`

At this point `instance/portal.conf` should resemble:

```properties
#------------------------------------------------
# Default MRDP application configuration settings
#------------------------------------------------

PORTAL_VERSION = 'localdev'
SERVER_NAME = 'localhost:5050'
DEBUG = True

# globus:
PORTAL_CLIENT_ID = 'SAMPLE'
PORTAL_CLIENT_SECRET = 'SAMPLE'
GLOBUS_AUTH_LOGOUT_URI = 'https://auth.globus.org/v2/web/logout'
GLOBUS_REDIRECT_URI_SCHEME = 'http'
SECRET_KEY = '=.DKwWzDd}!3}6yeAY+WTF#W:zt5msTI7]2`o}Y!ziU!#CYD+;T9JpW$ud|5C_3'

# SLATE API:
SLATE_API_TOKEN = 'SAMPLE'
SLATE_API_ENDPOINT = 'SAMPLE'

# Mailgun
MAILGUN_API_TOKEN = 'SAMPLE'
```

## Build and Run Portal

Running the image will create a new tagged container and start Portal.
* Below we use port `5050` due to port `5000` being reserved on MacOSX.

```shell
[your@localmachine]$ docker-compose up
 * Serving Flask app 'portal' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.2:5050/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

Point your browser to `http://localhost:5050`, make changes, and enjoy a live-preview experience.

### Podman Support

Build the image:

```shell
[your@localmachine]$ podman build --file ./resources/docker/Dockerfile --target local-stage --tag slate-portal:local .
[1/2] STEP 1/13: FROM rockylinux:9 AS base-stage
[1/2] STEP 2/13: ARG port
...
Successfully tagged localhost/slate-portal:local
6b0369b42beb01468615cbb17b2793bf2bc86e99e0b5dfd1fc2018eb3bde993a
```

Run the container:

```shell
[your@localmachine]$ podman run -it -v ${PWD}:/slate -p 5050:5050 slate-portal:local
 * Serving Flask app 'portal' (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
 * Running on all addresses.
   WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://172.17.0.2:5050/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 123-456-789
```

Point your browser to `http://localhost:5050`, make changes, and enjoy a live-preview experience.

## Teardown

1. Quit the Flask app (`CTRL + C`).
2. If you are using `docker`, refer to the [docker compose docs](https://docs.docker.com/compose/reference/) for appropriate commands.
3. Prune the now-stopped container to release system resources:

   ```shell
   [your@localmachine]$ docker container prune
   ```
   
   or:

   ```shell
   [your@localmachine]$ podman container prune
   ```
