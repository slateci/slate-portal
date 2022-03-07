# Local Development with Containers

A containerized Portal will provide a near live-preview developer experience.

## Requirements

### Install Docker

Install [Docker](https://docs.docker.com/get-docker/) for developing, managing, and running OCI containers on your system:

### Create `portal.conf`

Copy `instance/portal.conf.tmpl` to the following place in this project: `instance/portal.conf`. Complete the steps described below to modify properties and finalize this file.

### Register a globus Application

> **_IMPORTANT:_** Before proceeding ask the team about existing globus registrations as some localdev, development, and production projects and applications already exist.

Create your own App registration for use in the Portal.

* Visit the [Globus Developer Pages](https://developers.globus.org) to register an App.
* If this is your first time visiting the Developer Pages you will be asked to create a Project. A Project is a way to group Apps together.
* When registering the App you will be asked for some information, including the redirect URL and any scopes you will be requesting.
    * Redirect URL: `http://localhost:5000/authcallback`
* After creating your App the **Client ID** and **Client Secret** can be copied into this project in the following place:
    * `instance/portal.conf` in the `PORTAL_CLIENT_ID` and `PORTAL_CLIENT_SECRET` properties.

### Select a SLATE API Admin Account

Portal communicates with a SLATE API server via an admin account.

* Specify the SLATE API server in the following place of this project:
    * `instance/portal.conf` in the `SLATE_API_ENDPOINT` property.
* Ask the team for the API token of an appropriate admin account.
* Once in hand the token can be copied into this project in the following place:
    * `instance/portal.conf` in the `SLATE_API_TOKEN` property.

## Finalize `portal.conf`

At this point `instance/portal.conf` should resemble:

```properties
#------------------------------------------------
# Default MRDP application configuration settings
#------------------------------------------------

SERVER_NAME = '<your-value>'
DEBUG = True
SLATE_WEBSITE_LOGFILE = '/var/log/uwsgi/portal.log'

SECRET_KEY = '=.DKwWzDd}!3}6yeAY+WTF#W:zt5msTI7]2`o}Y!ziU!#CYD+;T9JpW$ud|5C_3'

# globus:
PORTAL_CLIENT_ID = '<your-value>'
PORTAL_CLIENT_SECRET = '<your-value>'
GLOBUS_AUTH_LOGOUT_URI = 'https://auth.globus.org/v2/web/logout'

# SLATE API:
SLATE_API_TOKEN = '<your-value>'
SLATE_API_ENDPOINT = '<your-value>'
```

## Build and Run Portal

Build the Docker image:

```shell
docker build -f Dockerfile -t slate-portal:local .
```

Running the image will create a new tagged container and start Portal:

```shell
[your@localmachine]$ docker run -it -v ${PWD}:/etc/slate/slate-website-python -p 5000:5000 slate-portal:local
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

Point your browser to `http://localhost:5000`, make changes, and enjoy a live-preview experience.

## Teardown

Quit the Flask app (`CTRL + C`) and prune the now-stopped Docker container to release system resources:

```shell
docker container prune
```

For more information on pruning stopped containers see [docker container prune](https://docs.docker.com/engine/reference/commandline/container_prune/)